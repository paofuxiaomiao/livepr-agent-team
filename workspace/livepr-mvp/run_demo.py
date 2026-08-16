#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from livepr.gateway import HttpScenarioGateway, LocalScenarioGateway
from livepr.orchestrator import LivePROrchestrator
from livepr.render import render_dashboard, render_markdown


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the LivePR deterministic Agent Team MVP")
    parser.add_argument("--scenario", default="product_delay_rumor")
    parser.add_argument("--approve", action="store_true", help="Simulate a named human approval")
    parser.add_argument("--approved-by", default="demo-reviewer")
    parser.add_argument("--gateway-url", help="Use the mock HTTP gateway instead of local JSON")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gateway = HttpScenarioGateway(args.gateway_url) if args.gateway_url else LocalScenarioGateway()
    if args.list:
        print("\n".join(gateway.list_scenarios()))
        return 0

    result = LivePROrchestrator(gateway).run(
        args.scenario,
        approved=args.approve,
        approved_by=args.approved_by if args.approve else None,
    )
    output_dir = args.output_dir or PROJECT_ROOT / "evidence" / args.scenario
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "agent-trace.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in result["agent_trace"]) + "\n",
        encoding="utf-8",
    )
    (output_dir / "host-card.txt").write_text(result["host_card"]["script"] + "\n", encoding="utf-8")
    (output_dir / "report.md").write_text(render_markdown(result), encoding="utf-8")
    (output_dir / "dashboard.html").write_text(render_dashboard(result), encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "scenario_id": result["scenario_id"],
        "trace_id": result["trace_id"],
        "risk_level": result["risk"]["risk_level"],
        "approval": result["safety_review"]["decision"],
        "output_dir": str(output_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
