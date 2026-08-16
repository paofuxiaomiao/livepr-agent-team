from __future__ import annotations

from collections import Counter
from typing import Any


VALID_SENTIMENTS = {"negative", "neutral", "positive"}
RISK_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def ratio(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def trend_burst_detect(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize sentiment, sources, topics and the latest negative burst."""
    if not events:
        raise ValueError("trend-burst-detect requires at least one event")
    invalid = [row.get("id") for row in events if row.get("sentiment") not in VALID_SENTIMENTS]
    if invalid:
        raise ValueError(f"invalid sentiment labels in events: {invalid}")
    sentiments = Counter(row["sentiment"] for row in events)
    topics = Counter(row.get("topic", "unknown") for row in events)
    sources = Counter(row.get("source", "unknown") for row in events)
    window = events[-min(5, len(events)) :]
    latest_negative = sum(row["sentiment"] == "negative" for row in window)
    top_topic, top_topic_count = topics.most_common(1)[0]
    return {
        "sample_size": len(events),
        "sentiment_counts": dict(sentiments),
        "negative_ratio": ratio(sentiments["negative"], len(events)),
        "latest_window_size": len(window),
        "latest_negative_ratio": ratio(latest_negative, len(window)),
        "top_topic": top_topic,
        "top_topic_share": ratio(top_topic_count, len(events)),
        "source_counts": dict(sources),
        "evidence_event_ids": [row["id"] for row in events],
    }


def fact_check(focus_fact_id: str, facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve the focal claim against an explicit event fact base."""
    match = next((row for row in facts if row.get("fact_id") == focus_fact_id), None)
    if not match:
        return {
            "fact_id": focus_fact_id,
            "status": "insufficient_evidence",
            "confidence": 0.0,
            "claim": "unknown",
            "truth": "暂无足够证据，禁止下结论。",
            "source": None,
            "response_points": [],
        }
    required = {"status", "claim", "truth", "source", "confidence"}
    missing = sorted(required - match.keys())
    if missing:
        raise ValueError(f"fact {focus_fact_id!r} is missing: {', '.join(missing)}")
    return {**match, "response_points": list(match.get("response_points", []))}


def risk_grade(trend: dict[str, Any], checked_fact: dict[str, Any]) -> dict[str, Any]:
    """Assign a transparent P1-P3 risk level from trend and evidence."""
    negative = trend["negative_ratio"]
    latest = trend["latest_negative_ratio"]
    fact_status = checked_fact["status"]
    if fact_status == "insufficient_evidence":
        level = "P1"
        reason = "关键信息缺少证据，公开回应风险高。"
    elif negative >= 0.6 or latest >= 0.8:
        level = "P1"
        reason = "负面信号集中且仍在最新窗口持续。"
    elif negative >= 0.4:
        level = "P2"
        reason = "负面讨论已形成，需要尽快回应。"
    else:
        level = "P3"
        reason = "讨论可控，持续观察并准备口径。"
    return {
        "risk_level": level,
        "reason": reason,
        "approval_required": level in {"P0", "P1", "P2"},
        "inputs": {
            "negative_ratio": negative,
            "latest_negative_ratio": latest,
            "fact_status": fact_status,
        },
    }


def response_plan(
    event: dict[str, Any], checked_fact: dict[str, Any], risk: dict[str, Any]
) -> dict[str, Any]:
    """Create three bounded response options with a recommended choice."""
    points = checked_fact.get("response_points") or [checked_fact["truth"]]
    common = {
        "evidence_fact_id": checked_fact["fact_id"],
        "risk_level": risk["risk_level"],
    }
    strategies = [
        {
            **common,
            "strategy_id": "S1",
            "name": "立即澄清并给出明确事实",
            "action": "主持人在下一次自然停顿时澄清，并说明可核验时间点。",
            "tradeoff": "响应最快；必须由负责人确认事实口径。",
            "response_points": points,
        },
        {
            **common,
            "strategy_id": "S2",
            "name": "先承认疑问，再在固定节点统一回应",
            "action": "主持人先确认已收到问题，在议程节点给出完整说明。",
            "tradeoff": "事实准备更充分；等待期间风险可能继续扩散。",
            "response_points": points,
        },
        {
            **common,
            "strategy_id": "S3",
            "name": "转入官方说明渠道",
            "action": "主持人口头给出最小事实，同时引导查看现场大屏或官方说明。",
            "tradeoff": "口径稳定；现场即时安抚效果较弱。",
            "response_points": points,
        },
    ]
    recommended = "S1" if risk["risk_level"] in {"P0", "P1"} else "S2"
    return {
        "event_id": event["event_id"],
        "recommended_strategy_id": recommended,
        "strategies": strategies,
    }


def host_card(
    event: dict[str, Any], checked_fact: dict[str, Any], strategy: dict[str, Any]
) -> dict[str, Any]:
    """Generate a concise presenter card from approved facts only."""
    points = checked_fact.get("response_points") or [checked_fact["truth"]]
    lead = event.get("host_card_lead", "刚才现场出现了一个值得澄清的问题。")
    close = event.get("host_card_close", "请以现场大屏和官方后续说明为准。")
    script = f"{lead}{'；'.join(points)}。{close}"
    return {
        "strategy_id": strategy["strategy_id"],
        "script": script,
        "character_count": len(script),
        "evidence_fact_ids": [checked_fact["fact_id"]],
        "delivery_target": "presenter-console",
    }


def safety_review(
    card: dict[str, Any], prohibited_terms: list[str], risk: dict[str, Any]
) -> dict[str, Any]:
    """Block unsupported, overlong or unapproved public language."""
    hits = [term for term in prohibited_terms if term and term in card["script"]]
    checks = {
        "has_evidence": bool(card.get("evidence_fact_ids")),
        "within_length_limit": card.get("character_count", 9999) <= 180,
        "prohibited_term_hits": hits,
        "external_auto_publish": False,
    }
    passed = checks["has_evidence"] and checks["within_length_limit"] and not hits
    return {
        "passed": passed,
        "approval_required": risk["approval_required"],
        "checks": checks,
        "decision": "awaiting_human_approval" if passed else "blocked_for_revision",
    }


def postmortem(
    before_events: list[dict[str, Any]],
    after_events: list[dict[str, Any]],
    state_history: list[str],
) -> dict[str, Any]:
    """Compare simulated before/after signals and preserve the state trail."""
    before = trend_burst_detect(before_events)
    after = trend_burst_detect(after_events)
    delta = round(after["negative_ratio"] - before["negative_ratio"], 4)
    return {
        "measurement_scope": "deterministic mock scenario; not a real-world outcome",
        "before_negative_ratio": before["negative_ratio"],
        "after_negative_ratio": after["negative_ratio"],
        "negative_ratio_delta": delta,
        "signal_improved": delta < 0,
        "before_sample_size": before["sample_size"],
        "after_sample_size": after["sample_size"],
        "state_history": state_history,
        "feedback_event_ids": after["evidence_event_ids"],
    }
