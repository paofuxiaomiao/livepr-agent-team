from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .agents import (
    CollectionAgent,
    FactCheckAgent,
    HostCardAgent,
    PostmortemAgent,
    SafetyAgent,
    StrategyAgent,
    TrendAgent,
)


class LivePROrchestrator:
    """Deterministic Team Leader implementing the LivePR state machine."""

    TEAM_LEADER = "livepr-team-leader"

    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway
        self.collection = CollectionAgent()
        self.trend = TrendAgent()
        self.fact_check = FactCheckAgent()
        self.strategy = StrategyAgent()
        self.host_card = HostCardAgent()
        self.safety = SafetyAgent()
        self.postmortem = PostmortemAgent()

    @staticmethod
    def _trace_id(scenario_id: str) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        suffix = hashlib.sha256(f"{scenario_id}:{timestamp}".encode()).hexdigest()[:10]
        return f"LIVEPR-{scenario_id.upper()}-{suffix}"

    def run(
        self,
        scenario_id: str,
        *,
        approved: bool = False,
        approved_by: str | None = None,
    ) -> dict[str, Any]:
        trace_id = self._trace_id(scenario_id)
        started_at = datetime.now(timezone.utc).isoformat()
        state_history = ["RECEIVED"]
        agent_trace: list[dict[str, Any]] = []

        def record(agent: str, skill_names: list[str], state: str, output: Any) -> None:
            state_history.append(state)
            digest = hashlib.sha256(
                json.dumps(output, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()[:16]
            agent_trace.append(
                {
                    "seq": len(agent_trace) + 1,
                    "agent": agent,
                    "skills": skill_names,
                    "state": state,
                    "output_digest": digest,
                }
            )

        collected = self.collection.run(self.gateway, scenario_id)
        record(self.collection.identity, self.collection.skills, "COLLECTED", collected)

        trend = self.trend.run(collected["events"])
        record(self.trend.identity, self.trend.skills, "TRIAGED", trend)

        policy = self.gateway.get_policy(scenario_id)
        checked_fact = self.fact_check.run(self.gateway, scenario_id, policy["focus_fact_id"])
        record(self.fact_check.identity, self.fact_check.skills, "VERIFIED", checked_fact)

        strategy = self.strategy.run(collected["event"], trend, checked_fact)
        record(self.strategy.identity, self.strategy.skills, "PLANNED", strategy)

        card = self.host_card.run(collected["event"], checked_fact, strategy["plan"])
        record(self.host_card.identity, self.host_card.skills, "CARD_DRAFTED", card)

        safety = self.safety.run(
            card,
            policy["prohibited_terms"],
            strategy["risk"],
            approved,
            approved_by,
        )
        state = "DELIVERED" if safety["delivered"] else "AWAITING_APPROVAL"
        record(self.safety.identity, self.safety.skills, state, safety)

        result: dict[str, Any] = {
            "schema_version": "livepr-run-v1",
            "trace_id": trace_id,
            "scenario_id": scenario_id,
            "started_at": started_at,
            "team_leader": self.TEAM_LEADER,
            "status": "awaiting_approval",
            "state_history": state_history,
            "event": collected["event"],
            "trend": trend,
            "fact_check": checked_fact,
            "risk": strategy["risk"],
            "response_plan": strategy["plan"],
            "host_card": card,
            "safety_review": safety,
            "postmortem": None,
            "agent_trace": agent_trace,
            "gateway_calls": self.gateway.calls,
            "evidence_chain": {
                "event_ids": trend["evidence_event_ids"],
                "fact_ids": card["evidence_fact_ids"],
                "agent_output_digests": [row["output_digest"] for row in agent_trace],
            },
        }

        if not safety["delivered"]:
            return result

        postmortem = self.postmortem.run(
            self.gateway, scenario_id, collected["events"], state_history + ["MONITORING"]
        )
        record(self.postmortem.identity, self.postmortem.skills, "CLOSED", postmortem)
        result.update(
            {
                "status": "closed",
                "state_history": state_history,
                "postmortem": postmortem,
                "agent_trace": agent_trace,
                "gateway_calls": self.gateway.calls,
                "evidence_chain": {
                    "event_ids": trend["evidence_event_ids"] + postmortem["feedback_event_ids"],
                    "fact_ids": card["evidence_fact_ids"],
                    "agent_output_digests": [row["output_digest"] for row in agent_trace],
                },
            }
        )
        return result
