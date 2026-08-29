# mcp-ess-proposal

Open-source MCP Server（开源 MCP 服务） for deterministic solar and energy-storage proposal calculations.

## Status

Version（版本）: **0.2.0**. MCP Tool Contract（MCP 工具契约）: **Core v0.2**.

The package version tracks the tool contract version. The first public release is `0.2.0`, not `0.1.0`, because the Core v0.2 contract carries changes that a strict Core v0.1 consumer can observe.

This repository is developed through `ai-codeops-harness` governance. Core v0 includes the deterministic Core, neutral fixtures, and a stdio MCP server adapter for the accepted Core v0 tool. PLAN-0001 migration passed human final review, and PLAN-0002 release preparation is approved and under way.

Release Candidate means the Core v0 scope, MCP Tool Contract（MCP 工具契约）, and stdio runtime are validated, but the package has not been published to a package index and no public release has been tagged.

## Quick Start

Prerequisite: Python 3.11 or newer.

Install from source:

```bash
python -m pip install -e .
```

Run the MCP server from a source checkout:

```bash
PYTHONPATH=src python -m mcp_ess_proposal
```

Equivalent installed console script:

```bash
mcp-ess-proposal
```

MCP clients should connect over stdio and call `generate_ess_proposal` with structured inputs. Example arguments:

```json
{
  "customer_type": "residential",
  "location": "Selangor",
  "monthly_kwh": 600,
  "tariff_myr_per_kwh": 0.60
}
```

`tariff_myr_per_kwh` is optional. When omitted, the server uses its bundled default tariff data and reports which source was used.

## Core Scope

Core v0 provides:

- MCP Server（MCP 服务）.
- MCP Tool Contract（MCP 工具契约）.
- Neutral sample data fixtures.
- Deterministic Calculation（确定性计算） from structured inputs.

Core v0 does not include:

- Lead（线索） capture.
- CRM writes.
- Private platform database writes.
- OCR / LLM provider calls.
- Prompt（提示词） or Skill（技能） logic.
- Runtime uploads or local image processing.

## Tool Contract

The accepted Core v0 tool contract is documented in [docs/contracts/mcp-tools.md](docs/contracts/mcp-tools.md).

Core v0.2 exposes one public tool:

- `generate_ess_proposal`

Behaviour worth knowing before you call it:

- **Consumption precedence** — `monthly_kwh` is the authoritative measurement and is never overridden by a value derived from `monthly_bill_myr`. Supply only one when you can.
- **Consistency validation** — if you supply both and they disagree by more than 10%, the tool returns `INCONSISTENT_CONSUMPTION_INPUT` rather than silently choosing one. The error `details` carry the implied bill, the resolved tariff, and the deviation.
- **Tariff source** — every successful response reports `tariff_source` as `user_provided`, `default_residential_tiered`, or `default_non_residential`.
- **Investment scope** — `financial.investment_scope` is always `pv_only`. Storage is sized when requested but is **not** priced, so `estimated_investment_myr` is not a whole-system cost.

Excluded from Core v0:

- `submit_consultation_lead`
- `generate_ess_proposal_from_bill`
- `hello`

## Configuration

Core v0 has no required runtime secrets.

Required environment variables: none.

The runtime does not load `.env` files or read provider, OCR / LLM, CRM, or database settings. `.env.example` is intentionally variable-free and exists only to make that zero-secret contract explicit.

## Data

Core v0 data fixtures are documented in [docs/data/fixtures.md](docs/data/fixtures.md). They are neutral sample values for validation, not official tariffs or quotations.

## Runtime Path

- Host / MCP Client starts `mcp_ess_proposal` over stdio.
- `src/mcp_ess_proposal/server.py` registers `generate_ess_proposal`.
- The MCP handler validates input through the SDK schema path and delegates to `src/mcp_ess_proposal/calculator.py`.
- `calculator.py` uses `models.py` and package fixtures loaded by `data.py`.
- The server returns contract-shaped structured content.

The calculator, models, data loader, and fixtures do not depend on the MCP SDK.

## Development

The MCP server runs over stdio for Core v0:

```bash
PYTHONPATH=src python -m mcp_ess_proposal
```

The server registers only the accepted `generate_ess_proposal` tool. Remote HTTP, authentication, OCR / LLM, provider integrations, and private adapters are outside Core v0.

```bash
python -m compileall src tests
PYTHONPATH=src python -m unittest discover -s tests
```

`tests/test_server.py` and `tests/test_stdio_runtime.py` require the `mcp` SDK, which is installed with the package. The remaining tests run without it.

## Continuous Integration

`.github/workflows/ci.yml` runs a single test-only job on Python 3.11, the minimum supported version. It performs:

- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- a distribution build
- an installed-wheel check that the bundled fixtures are present

The workflow requests read-only repository permissions and defines no secrets, deployment, or publishing steps.

## License

Released under the MIT License. See [LICENSE](LICENSE).

## Support Boundaries

- Supported（支持）: stdio transport, the accepted `generate_ess_proposal` tool, Python 3.11 or newer.
- Not implemented（未实现）: storage pricing, total system investment, and battery ROI. `financial.investment_scope` marks this explicitly.
- Not supported（不支持）: Remote HTTP（远程 HTTP） transport, authentication, provider / OCR / LLM integration, CRM or database writes, and Lead（线索） capture. These are outside Core v0 and are not planned in this repository.
- Fixture values are neutral samples for validation. They are not official tariffs or commercial quotations, and must not be used as a basis for pricing decisions.

## Governance

Current governing artifacts:

- [ADR-0001](docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md)
- [PLAN-0001](docs/plan/PLAN-0001-mcp-ess-open-source-migration.md)
- [PLAN-0002](docs/plan/PLAN-0002-release-preparation.md)
- [MCP Tool Contracts](docs/contracts/mcp-tools.md) (Core v0.2)
- [Contract AMENDMENT-0001](docs/contracts/AMENDMENT-0001-generate-ess-proposal-consumption-and-tariff.md)
- [PLAN-0003](docs/plan/PLAN-0003-contract-v0-2-implementation.md)

Current Harness recovery artifacts:

- [.ai/state/execution-state.yaml](.ai/state/execution-state.yaml)
- [docs/handoff/HANDOFF-current.md](docs/handoff/HANDOFF-current.md)
- [docs/harness/HARNESS-GAPS.md](docs/harness/HARNESS-GAPS.md)
