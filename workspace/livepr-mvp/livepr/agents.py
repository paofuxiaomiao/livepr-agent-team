from __future__ import annotations

from typing import Any

from . import skills


class CollectionAgent:
    identity = "collection-agent"
    # Input normalization is a built-in adapter responsibility rather than one
    # of the six reusable decision Skills submitted with the project.
    skills: list[str] = []

    def run(self, gateway: Any, scenario_id: str) -> dict[str, Any]:
        event = gateway.get_event(scenario_id)
        events = gateway.get_events(scenario_id)
        return {"event": event, "events": events, "normalized_count": len(events)}


class TrendAgent:
    identity = "trend-agent"
    skills = ["trend-burst-detect"]

    def run(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return skills.trend_burst_detect(events)


class FactCheckAgent:
    identity = "fact-check-agent"
    skills = ["fact-check"]

    def run(self, gateway: Any, scenario_id: str, focus_fact_id: str) -> dict[str, Any]:
        return skills.fact_check(focus_fact_id, gateway.get_facts(scenario_id))


class StrategyAgent:
    identity = "strategy-agent"
    skills = ["risk-grade", "response-plan"]

    def run(
        self, event: dict[str, Any], trend: dict[str, Any], checked_fact: dict[str, Any]
    ) -> dict[str, Any]:
        risk = skills.risk_grade(trend, checked_fact)
        plan = skills.response_plan(event, checked_fact, risk)
        return {"risk": risk, "plan": plan}


class HostCardAgent:
    identity = "host-card-agent"
    skills = ["host-card"]

    def run(
        self,
        event: dict[str, Any],
        checked_fact: dict[str, Any],
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        selected = next(
            strategy
            for strategy in plan["strategies"]
            if strategy["strategy_id"] == plan["recommended_strategy_id"]
        )
        return skills.host_card(event, checked_fact, selected)


class SafetyAgent:
    identity = "safety-agent"
    skills = ["risk-grade", "host-card"]

    def run(
        self,
        card: dict[str, Any],
        prohibited_terms: list[str],
        risk: dict[str, Any],
        approved: bool,
        approved_by: str | None,
    ) -> dict[str, Any]:
        review = skills.safety_review(card, prohibited_terms, risk)
        if not review["passed"]:
            return {**review, "approved": False, "approved_by": None, "delivered": False}
        if review["approval_required"] and not approved:
            return {**review, "approved": False, "approved_by": None, "delivered": False}
        return {
            **review,
            "decision": "approved_for_presenter_console",
            "approved": True,
            "approved_by": approved_by or "demo-reviewer",
            "delivered": True,
            "delivery_target": card["delivery_target"],
            "external_auto_publish": False,
        }


class PostmortemAgent:
    identity = "postmortem-agent"
    skills = ["postmortem"]

    def run(
        self,
        gateway: Any,
        scenario_id: str,
        before_events: list[dict[str, Any]],
        state_history: list[str],
    ) -> dict[str, Any]:
        return skills.postmortem(
            before_events,
            gateway.get_feedback(scenario_id),
            state_history,
        )
