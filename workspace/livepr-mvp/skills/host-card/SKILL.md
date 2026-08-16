# host-card

- Version：1.0.0
- Purpose：把已批准策略压缩成主持人可快速阅读的现场提词。
- Input：event lead/close、response_points、selected strategy。
- Output：script、character_count、evidence_fact_ids、delivery_target。
- Dependencies：fact-check、response-plan。
- Failure：超过180字则重写；没有 evidence_fact_ids 则拒绝生成。
- Reuse：主持提词、客服回复摘要、管理层应急口径。
- Boundary：不包含“绝对”“保证”等无证据承诺。
