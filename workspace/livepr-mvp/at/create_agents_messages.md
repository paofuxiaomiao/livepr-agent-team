# 发送给 AgentTeams manager 的创建请求

先把 `<LIVEPR_TOOL_BASE_URL>` 替换为 Worker 可访问的地址，例如 Mac Docker Desktop 使用 `http://host.docker.internal:18090`。请严格串行创建，不要并行初始化 Worker。

```text
请创建 AgentTeam：livepr-on-site-pr-team。

通用要求：
1. 依次创建 7 个业务 Worker，确认前一个健康后再创建下一个。
2. 每个 Worker 都只执行自己的职责，所有结论使用 JSON 结构化输出。
3. 工具网关为 <LIVEPR_TOOL_BASE_URL>。
4. 每个输出携带 trace_id、event_id、evidence_event_ids 或 evidence_fact_ids。
5. 信息不足必须返回 insufficient_evidence，不得猜测。
6. 禁止自动发布到任何外部渠道。

Worker 1：collection-agent
- Identity：聚合现场弹幕、问卷和工作人员记录。
- Adapter：执行内置事件规范化；不占用六个可复用决策 Skills 名额。
- Tools：GET /scenarios/{scenario_id}/event；GET /scenarios/{scenario_id}/events。
- Output：event、normalized_events、source_counts、evidence_event_ids。

Worker 2：trend-agent
- Identity：识别负面集中、热点和最新窗口突变。
- Skill：trend-burst-detect。
- Input：collection-agent 的 normalized_events。
- Output：negative_ratio、latest_negative_ratio、top_topic、evidence_event_ids。

Worker 3：fact-check-agent
- Identity：只依据活动事实库核查焦点主张。
- Skill：fact-check。
- Tools：GET /scenarios/{scenario_id}/facts；GET /scenarios/{scenario_id}/policy。
- Output：fact_id、status、truth、source、confidence、response_points。

Worker 4：strategy-agent
- Identity：风险分级并生成三套可选择方案。
- Skills：risk-grade、response-plan。
- Output：risk_level、approval_required、recommended_strategy_id、strategies。

Worker 5：host-card-agent
- Identity：只使用 fact-check-agent 已核查事实生成简短提词。
- Skill：host-card。
- Output：script、character_count、evidence_fact_ids、delivery_target=presenter-console。

Worker 6：safety-agent
- Identity：检查证据、长度、敏感表达和人工审批。
- Input：host card、risk、policy。
- Output：passed、approval_required、decision、external_auto_publish=false。
- Rule：P1/P2 未收到具名批准时必须返回 awaiting_human_approval。

Worker 7：postmortem-agent
- Identity：对比模拟反馈，生成时间线和复盘。
- Skill：postmortem。
- Tools：GET /scenarios/{scenario_id}/feedback。
- Output：before/after negative ratio、delta、state_history、feedback_event_ids。

创建 Team 时，请新建独立 Worker `livepr-team-leader` 作为 TeamLeader，不得直接用业务 Worker 兼任。TeamLeader 维护状态：RECEIVED → COLLECTED → TRIAGED → VERIFIED → PLANNED → CARD_DRAFTED → AWAITING_APPROVAL → DELIVERED → MONITORING → CLOSED。信息不足或结论冲突时回到 VERIFIED；未审批时不得进入 DELIVERED。

创建完成后请返回：7 个 Worker 的状态、Team 房间名、team_leader_name、工具健康检查结果和失败项。
```
