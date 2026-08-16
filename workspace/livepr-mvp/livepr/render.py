from __future__ import annotations

import html
import json
from typing import Any


def esc(value: Any) -> str:
    return html.escape(str(value))


def render_markdown(result: dict[str, Any]) -> str:
    postmortem = result.get("postmortem") or {}
    lines = [
        f"# LivePR 演示报告：{result['event']['title']}",
        "",
        f"- Trace ID：`{result['trace_id']}`",
        f"- 场景：`{result['scenario_id']}`（模拟数据）",
        f"- 状态：`{result['status']}`",
        f"- 风险等级：`{result['risk']['risk_level']}`",
        f"- 事实核查：`{result['fact_check']['status']}`",
        "",
        "## 主持人提词卡",
        "",
        result["host_card"]["script"],
        "",
        "## 安全门",
        "",
        f"- 人工审批要求：{result['safety_review']['approval_required']}",
        f"- 已批准：{result['safety_review']['approved']}",
        f"- 自动对外发布：{result['safety_review'].get('external_auto_publish', False)}",
    ]
    if postmortem:
        lines.extend(
            [
                "",
                "## 模拟反馈验证",
                "",
                f"- 回应前负面比例：{postmortem['before_negative_ratio']:.0%}",
                f"- 回应后负面比例：{postmortem['after_negative_ratio']:.0%}",
                f"- 变化：{postmortem['negative_ratio_delta']:.0%}",
                f"- 说明：{postmortem['measurement_scope']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Agent 执行轨迹",
            "",
            "| # | Agent | Skills | 状态 | 输出摘要 |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in result["agent_trace"]:
        lines.append(
            f"| {row['seq']} | {row['agent']} | {', '.join(row['skills'])} | "
            f"{row['state']} | `{row['output_digest']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render_dashboard(result: dict[str, Any]) -> str:
    postmortem = result.get("postmortem") or {}
    trend = result["trend"]
    strategies = result["response_plan"]["strategies"]
    agent_rows = "".join(
        f"<tr><td>{row['seq']}</td><td>{esc(row['agent'])}</td><td>{esc(', '.join(row['skills']))}</td>"
        f"<td>{esc(row['state'])}</td><td><code>{esc(row['output_digest'])}</code></td></tr>"
        for row in result["agent_trace"]
    )
    strategy_cards = "".join(
        f"<article class='strategy'><strong>{esc(row['strategy_id'])} · {esc(row['name'])}</strong>"
        f"<p>{esc(row['action'])}</p><small>{esc(row['tradeoff'])}</small></article>"
        for row in strategies
    )
    feedback = (
        f"<div class='metric'><b>{postmortem['before_negative_ratio']:.0%}</b><span>回应前负面</span></div>"
        f"<div class='metric'><b>{postmortem['after_negative_ratio']:.0%}</b><span>回应后负面</span></div>"
        f"<div class='metric good'><b>{postmortem['negative_ratio_delta']:.0%}</b><span>模拟变化</span></div>"
        if postmortem
        else "<div class='notice'>等待人工审批，尚未进入模拟反馈验证。</div>"
    )
    payload = html.escape(json.dumps(result, ensure_ascii=False, indent=2))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LivePR · {esc(result['event']['title'])}</title>
<style>
:root{{--navy:#1b1f3b;--orange:#ff6b35;--ink:#252a42;--muted:#68708a;--line:#dfe4ef;--bg:#f5f7fb;--green:#199b5b}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}}
header{{background:var(--navy);color:white;padding:36px max(5vw,28px)}} header h1{{margin:6px 0;font-size:36px}} header p{{margin:0;color:#cbd1e6}}
main{{max-width:1180px;margin:0 auto;padding:28px}} section{{background:white;border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:20px}}
.eyebrow{{color:var(--orange);font-weight:700;letter-spacing:.08em}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.metric{{background:#eef3ff;border-radius:12px;padding:18px}} .metric b{{display:block;font-size:32px}} .metric span{{color:var(--muted)}} .metric.good{{background:#eaf8f0;color:var(--green)}}
.card{{font-size:22px;border-left:6px solid var(--orange);background:#fff4ee;padding:18px;border-radius:10px}}
.strategy{{border:1px solid var(--line);border-radius:12px;padding:16px}} .strategy p{{margin:8px 0}} small{{color:var(--muted)}}
.notice{{padding:16px;background:#fff4ee;border-radius:10px;color:#9a3c16}} table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line)}} code{{font-size:12px}}
details pre{{white-space:pre-wrap;word-break:break-word;background:#101426;color:#dfe6ff;padding:16px;border-radius:10px;max-height:420px;overflow:auto}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}} header h1{{font-size:28px}}}}
</style>
</head>
<body>
<header><span class="eyebrow">LIVEPR · SIMULATED EVIDENCE</span><h1>{esc(result['event']['title'])}</h1><p>Trace ID {esc(result['trace_id'])} · {esc(result['status'])} · 所有数据均为脱敏模拟场景</p></header>
<main>
<section><span class="eyebrow">现场信号</span><h2>{esc(result['risk']['risk_level'])} 风险 · {trend['negative_ratio']:.0%} 负面占比</h2><div class="grid">{feedback}</div></section>
<section><span class="eyebrow">主持人提词卡</span><h2>经证据约束的现场表达</h2><div class="card">{esc(result['host_card']['script'])}</div><p>审批：{esc(result['safety_review']['decision'])}；自动对外发布：否。</p></section>
<section><span class="eyebrow">应对策略</span><h2>三套可选择路径</h2><div class="grid">{strategy_cards}</div></section>
<section><span class="eyebrow">执行证据</span><h2>Agent Team 状态轨迹</h2><table><thead><tr><th>#</th><th>Agent</th><th>Skills</th><th>状态</th><th>摘要</th></tr></thead><tbody>{agent_rows}</tbody></table></section>
<section><details><summary>查看完整结构化结果</summary><pre>{payload}</pre></details></section>
</main></body></html>"""
