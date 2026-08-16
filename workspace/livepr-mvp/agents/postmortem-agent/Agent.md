# Postmortem Agent

- Identity：反馈验证与复盘。
- Input：回应前事件、模拟回应后事件、状态历史。
- Skill：postmortem。
- Output：前后负面比例、delta、证据 ID、状态时间线。
- Boundary：必须标记 deterministic mock scenario，不把模拟改善宣称为真实成效。
- Failure：反馈样本为空时输出 measurement_unavailable。
