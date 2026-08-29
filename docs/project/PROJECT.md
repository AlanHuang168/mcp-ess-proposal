# Project Context

Status: Initial

Date: 2026-08-29

## Project

`mcp-ess-proposal` is an open-source MCP Server（开源 MCP 服务） for energy-storage proposal tooling.

## Scope

Core（核心） owns:

- MCP Server（MCP 服务）.
- MCP Tool Contract（MCP 工具契约）.
- Neutral Data Fixtures（中立数据样例）.
- Integration boundaries（集成边界）.
- Deterministic Calculation（确定性计算）.

Core excludes:

- the private platform brand.
- Lead（线索） capture.
- CRM routing.
- the private platform database writes.
- Skill（技能） and Prompt（提示词） logic.
- OCR / LLM adapters unless later approved.

## Source References

- Source project: `<PRIVATE_SOURCE_ROOT>`.
- Comparison project: `<PARTNER_PROJECT_ROOT>`.

## Governing Artifacts

- Accepted ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`.
- Approved PLAN: `docs/plan/PLAN-0001-mcp-ess-open-source-migration.md`.
- MCP Contract: `docs/contracts/mcp-tools.md`.
- System Map（系统图）: `docs/project/SYSTEM-MAP.md`.

## Current Runtime

- Server entrypoint: `src/mcp_ess_proposal/__main__.py`.
- MCP Server Adapter（MCP 服务适配层）: `src/mcp_ess_proposal/server.py`.
- Core deterministic calculation: `src/mcp_ess_proposal/calculator.py`.
- Domain models: `src/mcp_ess_proposal/models.py`.
- Neutral data loading and fixtures: `src/mcp_ess_proposal/data.py`, `src/mcp_ess_proposal/fixtures/*.json`.

Core v0 exposes only `generate_ess_proposal` over stdio and requires no environment variables or Secret（密钥）.

## Current Phase

PLAN-0001 Task 1 established the Core v0 MCP Tool Contract（MCP 工具契约）.

PLAN-0001 Task 2 created the open-source package scaffold without private brand, Lead（线索）, CRM, database, provider, OCR, or LLM coupling.

PLAN-0001 Task 3 migrated deterministic domain logic into neutral Core modules with contract-shaped outputs and unit tests.

PLAN-0001 Task 4 replaced embedded defaults with neutral package fixtures and documented fixture ownership.

PLAN-0001 Task 5 exposed the deterministic Core through a thin stdio MCP Server Adapter（MCP 服务适配层） that registers only `generate_ess_proposal`.

PLAN-0001 Task 6 aligned configuration declarations with runtime behavior: Core v0 has no required environment variables and no required Secret（密钥）.

PLAN-0001 Task 7 synchronized README, Project Context（项目上下文）, System Map（系统图）, Handoff（交接）, Runtime State（运行状态）, Checkpoint（检查点）, and Harness gap records with the current implementation.

PLAN-0001 Task 8 completed final Validation（验证）, package/runtime checks, secret-safe review, Scope Drift（范围漂移） review, and Harness state closeout. The migration slice is ready for Human Final Review（人工最终审核）.

PLAN-0001 was accepted as Complete（已完成） by Human Final Review on 2026-08-29. The current version is recognized as V0.1 Release Candidate（发布候选）.

Router selected PLAN for the next Release Preparation（发布准备） phase.

Current state（当前状态）, 2026-08-29: PLAN-0002 and PLAN-0003 are complete. The MCP Tool Contract is Core v0.2 and the project version is **0.2.0**. The statements above are the historical record of each phase and are not restated as current facts.
