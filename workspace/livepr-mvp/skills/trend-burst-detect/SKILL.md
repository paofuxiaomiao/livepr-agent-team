# trend-burst-detect

- Version：1.0.0
- Purpose：从规范化事件流计算情绪分布、最新窗口突变、热点与来源覆盖。
- Input：非空事件数组；每条含 id、source、topic、sentiment、text。
- Output：sample_size、negative_ratio、latest_negative_ratio、top_topic、source_counts、evidence_event_ids。
- Dependencies：无；Python 标准库 Counter。
- Failure：空数组或未知 sentiment 返回 validation_error。
- Reuse：直播弹幕、客服工单、论坛问卷、会议反馈。
- Test：`tests/test_livepr.py` 两个场景复用同一实现。
