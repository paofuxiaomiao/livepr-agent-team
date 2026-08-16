# LivePR MVP 复现与验证记录

验证日期：2026-08-16（北京时间）

## 验证结论

- `python3 -m unittest discover -s tests -v`：4 项测试全部通过。
- 未提供人工批准时，P1 流程停在 `awaiting_approval`，不会进入交付或复盘。
- 提供具名批准时，流程进入 `closed`，交付目标仅为 `presenter-console`，`external_auto_publish=false`。
- 同一套 Team、状态机和 6 个可复用 Skills 已复用于 2 个不同模拟场景。
- 本地 JSON Gateway 与 HTTP Gateway 两种传输路径均已跑通。
- 每次完整运行生成 5 项证据：`result.json`、`agent-trace.jsonl`、`host-card.txt`、`report.md`、`dashboard.html`。
- 仓库扫描未发现真实 API Key、Token、密码或私钥。

## 场景结果

| 证据目录 | 传输 | 审批 | 最终状态 | 模拟负面占比 |
| --- | --- | --- | --- | --- |
| `verified-product-delay` | local-json | 已批准 | `closed` | 66.67% → 20.00% |
| `verified-awaiting-approval` | local-json | 未批准 | `awaiting_approval` | 不执行后评估 |
| `verified-keynote-change` | local-json | 已批准 | `closed` | 60.00% → 12.50% |
| `verified-http` | http | 已批准 | `closed` | 66.67% → 20.00% |

以上占比来自确定性虚构场景，用于证明流程和证据链可运行，不代表真实活动效果，也不构成因果归因。

## 复现命令

```bash
python3 -m unittest discover -s tests -v
./verify.sh
```

HTTP 工具链：

```bash
./run_gateway.sh
curl http://127.0.0.1:18090/health
python3 run_demo.py --scenario product_delay_rumor --approve \
  --approved-by http-integration \
  --gateway-url http://127.0.0.1:18090 \
  --output-dir evidence/verified-http
```

## 证据定位

- 审批拦截：`evidence/verified-awaiting-approval/result.json`
- 完整闭环：`evidence/verified-product-delay/result.json`
- Agent Trace：`evidence/verified-product-delay/agent-trace.jsonl`
- 自包含结果页：`evidence/verified-product-delay/dashboard.html`
- HTTP 联调：`evidence/verified-http/result.json`
- 测试覆盖：`tests/test_livepr.py`

