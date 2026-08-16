# 舆情宝 LivePR：现场舆情监测与主持决策 Agent Team

LivePR 是一个面向发布会、论坛、直播和大型活动的多 Agent 决策闭环 MVP。它聚合模拟弹幕、问卷和现场记录，完成趋势研判、事实核查、风险分级、策略生成、主持人提词、安全审批和反馈复盘。

本仓库不是官方 Baseline 改名版本。代码、场景、Agent Identity、Skills、状态机、HTML 结果页和测试均围绕现场舆情场景重新实现。

## MVP 能证明什么

1. Team Leader 可以按状态机调度 7 类专职 Agent。
2. 每个关键结论都可追溯到事件 ID、事实 ID 和 Agent 输出摘要。
3. P1/P2 响应默认停在人工审批门，不会自动对外发布。
4. 同一套 Agent 与 Skills 可复用于两类不同活动场景。
5. 运行后生成 JSON、JSONL、主持提词、Markdown 报告和自包含 HTML 大屏。
6. 不需要 API Key；确定性执行路径便于评委复现。后续可把各 Agent 接入 AgentTeams LLM Worker。

## 角色与职责

| Agent | 主要职责 | 核心 Skill |
| --- | --- | --- |
| LivePR Team Leader | 拆解、路由、状态维护、冲突回退 | 状态机与证据汇总 |
| Collection Agent | 聚合并规范化现场信号 | 内置输入规范化（非独立 Skill） |
| Trend Agent | 识别负面集中、热点和最新窗口突变 | trend-burst-detect |
| Fact Check Agent | 用活动事实库核查焦点主张 | fact-check |
| Strategy Agent | 风险分级并生成三套应对路径 | risk-grade, response-plan |
| Host Card Agent | 只使用已核查事实生成短提词 | host-card |
| Safety Agent | 敏感词、证据、长度和人工审批检查 | risk-grade, host-card |
| Postmortem Agent | 比较模拟回应前后信号并生成复盘 | postmortem |

## 最短运行

环境：Python 3.10+，只使用标准库。

```bash
cd livepr-mvp
python3 -m unittest discover -s tests -v
python3 run_demo.py --scenario product_delay_rumor --approve --approved-by demo-reviewer
```

结果写入：

```text
evidence/product_delay_rumor/
├── result.json          # 完整结构化结果
├── agent-trace.jsonl    # 每个 Agent 的状态与输出摘要
├── host-card.txt        # 主持人提词卡
├── report.md            # 可读演示报告
└── dashboard.html       # 自包含实时大屏结果页
```

不带 `--approve` 时，系统必须停在人工审批：

```bash
python3 run_demo.py --scenario product_delay_rumor \
  --output-dir evidence/product_delay_rumor-awaiting
```

复用第二个场景：

```bash
python3 run_demo.py --scenario keynote_schedule_change --approve
```

## 通过 HTTP 工具网关运行

终端 1：

```bash
python3 tools/mock_event_gateway.py --host 127.0.0.1 --port 18090
```

终端 2：

```bash
curl http://127.0.0.1:18090/health
python3 run_demo.py --scenario product_delay_rumor --approve \
  --gateway-url http://127.0.0.1:18090 \
  --output-dir evidence/product_delay_rumor-http
```

AgentTeams Worker 位于 Docker 时，可将工具地址替换成 `http://host.docker.internal:18090`，并先从容器内验证 `/health`。

## 状态机

```text
RECEIVED
  → COLLECTED
  → TRIAGED
  → VERIFIED
  → PLANNED
  → CARD_DRAFTED
  → AWAITING_APPROVAL ──人工拒绝──→ 保持不发布
  → DELIVERED ──仅主持人控制台──→ MONITORING
  → CLOSED
```

信息不足时，`fact-check` 输出 `insufficient_evidence`，风险升级为 P1，禁止 Agent 擅自补全事实。所有外部发布能力均未实现，Safety Agent 的 `external_auto_publish` 永远为 `false`。

## AgentTeams 接入

- [at/AgentTeam.md](at/AgentTeam.md)：Team、状态和安全边界。
- [at/create_agents_messages.md](at/create_agents_messages.md)：发送给 AgentTeams manager 的自包含创建请求。
- [at/run_demo_task_message.md](at/run_demo_task_message.md)：发送到 Team 房间的任务消息。
- [at/team_spec.json](at/team_spec.json)：机器可读 Agent Identity、Skills 和工具契约。

本地确定性运行是可复现 fallback；比赛部署路径是 AgentTeams Team Leader + 7 个业务 Worker + HTTP/MCP 等价工具接口。创建 Worker 时按顺序串行创建，避免低规格环境并发初始化失败。

## 数据、权限与开源边界

- 两个场景均为虚构模拟数据，不包含真实个人信息。
- 真实渠道适配器、商业 API Key、闭源模型和活动私有事实库不进入仓库。
- 运行时只使用 Python 标准库；第三方边界见 [THIRD_PARTY.md](THIRD_PARTY.md)。
- 代码计划采用 Apache-2.0；正式开源前由参赛者确认团队和依赖授权。

## 当前限制

- 暂未连接真实微博、抖音、微信或直播平台 API。
- 情绪标签来自模拟场景，不代表真实模型准确率。
- 回应前后变化只证明流程可运行，不代表真实活动效果。
- 未配置 LLM 时使用确定性 Skill；接入 AgentTeams 后需补充模型评测、延迟和成本数据。
