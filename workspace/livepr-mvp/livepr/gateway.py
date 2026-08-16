from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO_DIR = PROJECT_ROOT / "scenarios"


class GatewayError(RuntimeError):
    """Raised when the scenario gateway cannot return valid data."""


class LocalScenarioGateway:
    """Read deterministic, privacy-safe scenarios from local JSON files."""

    def __init__(self, scenario_dir: Path | None = None) -> None:
        self.scenario_dir = scenario_dir or DEFAULT_SCENARIO_DIR
        self.calls: list[dict[str, Any]] = []

    def list_scenarios(self) -> list[str]:
        return sorted(path.stem for path in self.scenario_dir.glob("*.json"))

    def _load(self, scenario_id: str) -> dict[str, Any]:
        path = self.scenario_dir / f"{scenario_id}.json"
        if not path.exists():
            raise GatewayError(
                f"Unknown scenario {scenario_id!r}; available: {', '.join(self.list_scenarios())}"
            )
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        required = {"scenario_id", "event", "events", "facts", "feedback_events"}
        missing = sorted(required - payload.keys())
        if missing:
            raise GatewayError(f"Scenario {scenario_id!r} is missing fields: {', '.join(missing)}")
        if payload["scenario_id"] != scenario_id:
            raise GatewayError(f"Scenario id mismatch in {path}")
        return payload

    def _record(self, scenario_id: str, resource: str, value: Any) -> Any:
        count = len(value) if isinstance(value, list) else 1
        self.calls.append(
            {"transport": "local-json", "scenario_id": scenario_id, "resource": resource, "count": count}
        )
        return value

    def get_event(self, scenario_id: str) -> dict[str, Any]:
        return self._record(scenario_id, "event", self._load(scenario_id)["event"])

    def get_events(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._record(scenario_id, "events", self._load(scenario_id)["events"])

    def get_facts(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._record(scenario_id, "facts", self._load(scenario_id)["facts"])

    def get_feedback(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._record(scenario_id, "feedback_events", self._load(scenario_id)["feedback_events"])

    def get_policy(self, scenario_id: str) -> dict[str, Any]:
        data = self._load(scenario_id)
        return self._record(
            scenario_id,
            "policy",
            {
                "focus_fact_id": data["focus_fact_id"],
                "prohibited_terms": data.get("prohibited_terms", []),
                "expected": data.get("expected", {}),
            },
        )


class HttpScenarioGateway:
    """Use the same scenario contract through an HTTP gateway."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.calls: list[dict[str, Any]] = []

    def _get(self, scenario_id: str, resource: str) -> Any:
        url = f"{self.base_url}/scenarios/{quote(scenario_id)}/{resource}"
        try:
            with urlopen(url, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - exact transport error varies
            raise GatewayError(f"GET {url} failed: {exc}") from exc
        self.calls.append(
            {
                "transport": "http",
                "scenario_id": scenario_id,
                "resource": resource,
                "status": 200,
            }
        )
        return payload

    def list_scenarios(self) -> list[str]:
        url = f"{self.base_url}/scenarios"
        with urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["scenarios"]

    def get_event(self, scenario_id: str) -> dict[str, Any]:
        return self._get(scenario_id, "event")

    def get_events(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._get(scenario_id, "events")

    def get_facts(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._get(scenario_id, "facts")

    def get_feedback(self, scenario_id: str) -> list[dict[str, Any]]:
        return self._get(scenario_id, "feedback")

    def get_policy(self, scenario_id: str) -> dict[str, Any]:
        return self._get(scenario_id, "policy")
