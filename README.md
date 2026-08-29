# mcp-ess-proposal

`mcp-ess-proposal` 是一个开源 MCP Server（开源 MCP 服务），用于从结构化输入生成确定性的太阳能与储能初步方案计算结果。

## 状态

版本（Version）: **0.2.0**。MCP Tool Contract（MCP 工具契约）: **Core v0.2**。

包版本跟随工具契约版本。首次公开版本使用 `0.2.0`，而不是 `0.1.0`，因为 Core v0.2 契约包含严格 Core v0.1 消费者可观察到的变更。

本仓库通过 `ai-codeops-harness` 治理。Core v0 包含确定性计算核心、中立 fixtures，以及面向已接受 Core v0 工具的 stdio MCP Server Adapter（MCP 服务适配层）。

当前包尚未发布到 package index，也没有创建公开 release tag。

## 快速开始

前置要求：Python 3.11 或更新版本，MCP SDK 2.1 或更新版本。

从源码安装：

```bash
python -m pip install -e .
```

从源码 checkout 运行 MCP 服务：

```bash
PYTHONPATH=src python -m mcp_ess_proposal
```

安装后的等价命令：

```bash
mcp-ess-proposal
```

MCP Client（MCP 客户端）应通过 stdio 连接，并使用结构化输入调用 `generate_ess_proposal`。示例参数：

```json
{
  "customer_type": "residential",
  "location": "Selangor",
  "monthly_kwh": 600,
  "tariff_myr_per_kwh": 0.60
}
```

`tariff_myr_per_kwh` 是可选参数。未提供时，服务会使用内置默认电价数据，并在响应中声明使用的数据来源。

## Core 范围

Core v0 包含：

- MCP Server（MCP 服务）。
- MCP Tool Contract（MCP 工具契约）。
- 中立样例数据 fixtures。
- 基于结构化输入的 Deterministic Calculation（确定性计算）。

Core v0 不包含：

- Lead（线索）采集。
- CRM 写入。
- 私有平台数据库写入。
- OCR / LLM provider 调用。
- Prompt（提示词）或 Skill（技能）逻辑。
- 运行时上传或本地图片处理。

## 工具契约

已接受的 Core v0 工具契约见 [docs/contracts/mcp-tools.md](docs/contracts/mcp-tools.md)。

Core v0.2 只暴露一个 public tool（公开工具）：

- `generate_ess_proposal`

调用前需要了解的行为：

- **Consumption precedence（用电量优先级）**：`monthly_kwh` 是权威用电量输入，不会被从 `monthly_bill_myr` 推导出的值覆盖。能只提供一个输入时，建议只提供一个。
- **Consistency validation（一致性校验）**：如果同时提供 `monthly_kwh` 和 `monthly_bill_myr`，且两者偏差超过 10%，工具返回 `INCONSISTENT_CONSUMPTION_INPUT`，不会静默选择其中一个。错误响应的 `details` 包含推导电费、解析后的电价和偏差。
- **Tariff source（电价来源）**：每个成功响应都会返回 `tariff_source`，取值为 `user_provided`、`default_residential_tiered` 或 `default_non_residential`。
- **Investment scope（投资范围）**：`financial.investment_scope` 始终为 `pv_only`。如果请求备电，系统会给出储能容量建议，但不会计入储能价格，因此 `estimated_investment_myr` 不是完整系统总投资。
- **Protocol-required normalization（协议要求的规范化）**：MCP SDK 2.x runtime discovery 的 output schema 会在已接受 `oneOf` 分支外增加顶层 `type: "object"`。这是 [Contract AMENDMENT-0002](docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md) 授权的最小协议表示规范化，不改变业务契约语义。

Core v0 排除以下工具：

- `submit_consultation_lead`
- `generate_ess_proposal_from_bill`
- `hello`

## 配置

Core v0 不需要运行时密钥。

必需环境变量：无。

运行时不会加载 `.env` 文件，也不会读取 provider、OCR / LLM、CRM 或数据库配置。`.env.example` 故意不声明任何变量，用于明确零密钥运行契约。

## 数据

Core v0 数据 fixtures 见 [docs/data/fixtures.md](docs/data/fixtures.md)。这些值是用于验证的中立样例，不是官方电价或商业报价。

## 运行路径

- Host / MCP Client 通过 stdio 启动 `mcp_ess_proposal`。
- `src/mcp_ess_proposal/server.py` 注册 `generate_ess_proposal`。
- MCP handler 接收结构化参数并委托给 `src/mcp_ess_proposal/calculator.py`。
- `calculator.py` 使用 `models.py` 和由 `data.py` 加载的包内 fixtures。
- 服务返回符合契约形状的 structured content（结构化内容）。

`calculator.py`、`models.py`、`data.py` 和 fixtures 不依赖 MCP SDK。

## 开发

Core v0 的 MCP 服务通过 stdio 运行：

```bash
PYTHONPATH=src python -m mcp_ess_proposal
```

服务只注册已接受的 `generate_ess_proposal` 工具。Remote HTTP（远程 HTTP）、authentication（鉴权）、OCR / LLM、provider 集成和私有适配器均不属于 Core v0。

本地验证：

```bash
python -m compileall src tests
PYTHONPATH=src python -m unittest discover -s tests
```

`tests/test_server.py`、`tests/test_stdio_runtime.py` 和 `tests/test_stdio_runtime_v0_2.py` 需要 `mcp` SDK；该依赖会随包安装。其余测试不依赖 MCP SDK。

## 持续集成

`.github/workflows/ci.yml` 在 Python 3.11 上运行单一 test-only job（仅测试任务）。它执行：

- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- distribution build（分发构建）
- installed-wheel check（已安装 wheel 检查），确认包内 fixtures 存在

该 workflow 只请求 read-only repository permissions（只读仓库权限），不包含 secrets、部署或发布步骤。

## 许可证

本项目使用 MIT License。见 [LICENSE](LICENSE)。

## 支持边界

- Supported（支持）：stdio transport、已接受的 `generate_ess_proposal` 工具、Python 3.11 或更新版本、MCP SDK 2.1 或更新版本。
- Not implemented（未实现）：储能定价、完整系统总投资、电池 ROI。`financial.investment_scope` 会明确标记这一点。
- Not supported（不支持）：Remote HTTP（远程 HTTP）transport、authentication（鉴权）、provider / OCR / LLM 集成、CRM 或数据库写入、Lead（线索）采集。这些都在 Core v0 之外，本仓库当前不规划实现。
- Fixture values（样例数据值）只用于验证，不是官方电价或商业报价，不能作为定价决策依据。

## 治理

当前治理产物：

- [ADR-0001](docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md)
- [ADR-0002](docs/adr/ADR-0002-open-source-governance-artifact-boundary.md)
- [PLAN-0001](docs/plan/PLAN-0001-mcp-ess-open-source-migration.md)
- [PLAN-0002](docs/plan/PLAN-0002-release-preparation.md)
- [PLAN-0003](docs/plan/PLAN-0003-contract-v0-2-implementation.md)
- [MCP Tool Contracts](docs/contracts/mcp-tools.md)（Core v0.2）
- [Contract AMENDMENT-0001](docs/contracts/AMENDMENT-0001-generate-ess-proposal-consumption-and-tariff.md)
- [Contract AMENDMENT-0002](docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md)

当前 Harness recovery artifacts（Harness 恢复产物）：

- [.ai/state/execution-state.yaml](.ai/state/execution-state.yaml)
- [docs/handoff/HANDOFF-current.md](docs/handoff/HANDOFF-current.md)
- [docs/harness/HARNESS-GAPS.md](docs/harness/HARNESS-GAPS.md)
