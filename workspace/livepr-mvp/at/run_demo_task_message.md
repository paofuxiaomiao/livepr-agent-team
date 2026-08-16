# 发送到 LivePR Team 房间的演示任务

先在 Team 房间 `@<team_leader_name>`，再发送：

```text
请处理现场舆情事件：
scenario_id=product_delay_rumor
event_id=EVT-LIVEPR-001

目标：
1. 通过工具网关主动获取现场事件、评论流、事实库和政策；
2. 调度专职 Agent 完成趋势研判、事实核查、风险分级和三套策略；
3. 生成主持人提词卡，但在人工批准前不得交付；
4. 请先输出审批摘要并停在 AWAITING_APPROVAL；
5. 收到我回复“批准 S1，批准人=<姓名>”后，再交付主持人控制台并获取模拟反馈；
6. 最终报告必须包含 trace_id、状态历史、证据 ID、Agent 输出摘要、人工审批记录和模拟反馈说明。
```

审批消息示例：

```text
批准 S1，批准人=现场公关负责人（演示）
```
