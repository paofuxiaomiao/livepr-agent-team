# response-plan

- Version：1.0.0
- Purpose：为同一事件生成三套有取舍的应对路径。
- Input：event、fact check、risk grade。
- Output：recommended_strategy_id、strategies[]；每套含 action、tradeoff、evidence_fact_id。
- Dependencies：risk-grade、fact-check。
- Failure：证据冲突时不推荐策略，请 Team Leader 回退核查。
- Reuse：发布会主持、直播运营、会议应急、客服升级。
- Boundary：只规划，不执行、不发布。
