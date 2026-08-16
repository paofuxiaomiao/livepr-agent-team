# postmortem

- Version：1.0.0
- Purpose：对比回应前后模拟信号并保留状态和证据链。
- Input：before events、after events、state history。
- Output：before/after negative ratio、delta、signal_improved、feedback_event_ids。
- Dependencies：trend-burst-detect。
- Failure：反馈为空时 measurement_unavailable，不宣称改善。
- Reuse：舆情复盘、客服处置、活动运营、事故响应。
- Disclosure：当前输出必须标记 deterministic mock scenario，不代表真实因果效果。
