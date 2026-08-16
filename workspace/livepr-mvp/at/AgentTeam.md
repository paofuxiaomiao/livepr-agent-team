# LivePR AgentTeam

## Team 形态

- Team：`livepr-on-site-pr-team`
- Team Leader：`livepr-team-leader`，由 manager 在创建 Team 时生成独立 Worker。
- Business Workers：7 个，按 `collection → trend → fact-check → strategy → host-card → safety → postmortem` 串行创建。
- Worker Runtime：优先使用 AgentTeams 当前稳定版本支持的 QwenPaw/CoPaw 类运行时。
- 工具入口：HTTP `http://<TOOL_HOST>:18090`，可映射为 MCP 工具。

## 状态与所有权

| 状态 | Owner | 输出 | 失败路径 |
| --- | --- | --- | --- |
| RECEIVED | Team Leader | event_id, trace_id | 输入不完整则向用户补问 |
| COLLECTED | Collection | normalized events | 数据源不可用则标记缺口 |
| TRIAGED | Trend | topic, negative ratio, evidence IDs | 标签异常则停止 |
| VERIFIED | Fact Check | fact status, truth, source | 无证据输出 insufficient_evidence |
| PLANNED | Strategy | P1-P3, 3 strategies | 冲突回 VERIFIED |
| CARD_DRAFTED | Host Card | short script + fact IDs | 超长则重写 |
| AWAITING_APPROVAL | Safety | review checklist | 未批准不交付 |
| DELIVERED | Safety | presenter-console receipt | 禁止自动对外发布 |
| CLOSED | Postmortem | before/after + report | 数据不足标记不可判断 |

## 安全边界

1. Agent 不能补造活动事实。
2. 所有提词必须绑定事实 ID。
3. P1/P2 必须人工批准。
4. 交付目标仅为主持人控制台；不实现社交平台自动发布。
5. 真实数据接入前必须脱敏并确认授权。
