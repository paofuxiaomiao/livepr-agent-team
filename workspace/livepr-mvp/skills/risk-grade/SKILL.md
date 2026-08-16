# risk-grade

- Version：1.0.0
- Purpose：用透明规则将趋势和事实状态映射为 P1-P3。
- Input：negative_ratio、latest_negative_ratio、fact status。
- Output：risk_level、reason、approval_required、inputs。
- Dependencies：trend-burst-detect、fact-check 输出契约。
- Failure：insufficient_evidence 自动升级为 P1，不允许降级。
- Reuse：现场舆情、客服升级、内容审核、事件响应。
- Governance：阈值必须版本化；真实部署前需用评测集校准。
