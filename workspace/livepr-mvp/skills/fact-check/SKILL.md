# fact-check

- Version：1.0.0
- Purpose：将焦点主张与活动事实库中的具名记录对齐。
- Input：focus_fact_id、facts[]。
- Output：fact_id、status、truth、source、confidence、response_points。
- Dependencies：只读活动事实库。
- Failure：找不到 fact_id 时返回 insufficient_evidence，不生成替代事实。
- Reuse：活动口径、产品发布、议程变更、嘉宾信息核查。
- Audit：所有提词必须携带本 Skill 输出的 evidence_fact_ids。
