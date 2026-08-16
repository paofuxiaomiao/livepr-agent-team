#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = PROJECT_ROOT / "scenarios"


def load_scenario(scenario_id: str) -> dict:
    path = SCENARIO_DIR / f"{scenario_id}.json"
    if not path.exists():
        raise FileNotFoundError(scenario_id)
    return json.loads(path.read_text(encoding="utf-8"))


class Handler(BaseHTTPRequestHandler):
    server_version = "LivePRMockGateway/1.0"

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parts = [unquote(part) for part in urlparse(self.path).path.strip("/").split("/") if part]
        if parts == ["health"]:
            self._json(200, {"ok": True, "service": "livepr-mock-event-gateway"})
            return
        if parts == ["scenarios"]:
            self._json(200, {"scenarios": sorted(path.stem for path in SCENARIO_DIR.glob("*.json"))})
            return
        if len(parts) == 3 and parts[0] == "scenarios":
            scenario_id, resource = parts[1], parts[2]
            try:
                scenario = load_scenario(scenario_id)
            except FileNotFoundError:
                self._json(404, {"error": "unknown_scenario", "scenario_id": scenario_id})
                return
            mapping = {
                "event": scenario["event"],
                "events": scenario["events"],
                "facts": scenario["facts"],
                "feedback": scenario["feedback_events"],
                "policy": {
                    "focus_fact_id": scenario["focus_fact_id"],
                    "prohibited_terms": scenario.get("prohibited_terms", []),
                    "expected": scenario.get("expected", {}),
                },
            }
            if resource not in mapping:
                self._json(404, {"error": "unknown_resource", "resource": resource})
                return
            self._json(200, mapping[resource])
            return
        self._json(404, {"error": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        print(f"[gateway] {self.address_string()} {format % args}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18090)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"ok": True, "url": f"http://{args.host}:{args.port}"}, ensure_ascii=False))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
