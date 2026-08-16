from __future__ import annotations

import unittest

from livepr.gateway import LocalScenarioGateway
from livepr.orchestrator import LivePROrchestrator
from livepr.render import render_dashboard


class LivePRFlowTests(unittest.TestCase):
    def test_human_gate_blocks_delivery_without_approval(self) -> None:
        result = LivePROrchestrator(LocalScenarioGateway()).run("product_delay_rumor")
        self.assertEqual("awaiting_approval", result["status"])
        self.assertEqual("P1", result["risk"]["risk_level"])
        self.assertFalse(result["safety_review"]["delivered"])
        self.assertNotIn("CLOSED", result["state_history"])
        self.assertIsNone(result["postmortem"])

    def test_approved_flow_closes_with_evidence_and_feedback(self) -> None:
        result = LivePROrchestrator(LocalScenarioGateway()).run(
            "product_delay_rumor", approved=True, approved_by="unit-test-reviewer"
        )
        self.assertEqual("closed", result["status"])
        self.assertEqual("misleading", result["fact_check"]["status"])
        self.assertEqual("S1", result["response_plan"]["recommended_strategy_id"])
        self.assertTrue(result["safety_review"]["approved"])
        self.assertFalse(result["safety_review"]["external_auto_publish"])
        self.assertTrue(result["postmortem"]["signal_improved"])
        self.assertEqual(7, len(result["agent_trace"]))
        self.assertEqual("CLOSED", result["state_history"][-1])
        self.assertGreater(len(result["evidence_chain"]["event_ids"]), 10)

    def test_second_scenario_uses_same_team_and_skills(self) -> None:
        result = LivePROrchestrator(LocalScenarioGateway()).run(
            "keynote_schedule_change", approved=True
        )
        self.assertEqual("closed", result["status"])
        self.assertEqual("confirmed", result["fact_check"]["status"])
        self.assertIn("备用圆桌", result["host_card"]["script"])
        self.assertEqual(7, len({row["agent"] for row in result["agent_trace"]}))

    def test_dashboard_is_self_contained_and_auditable(self) -> None:
        result = LivePROrchestrator(LocalScenarioGateway()).run(
            "product_delay_rumor", approved=True
        )
        dashboard = render_dashboard(result)
        self.assertIn("<!doctype html>", dashboard.lower())
        self.assertIn(result["trace_id"], dashboard)
        self.assertIn("SIMULATED EVIDENCE", dashboard)
        self.assertIn("自动对外发布：否", dashboard)


if __name__ == "__main__":
    unittest.main()
