# PLAN-0001: MCP ESS Open Source Migration

Status: Complete

Date: 2026-08-29

Completed: 2026-08-29

Completion Basis（完成依据）:

- Human Final Review（人工最终审核） accepted PLAN-0001.
- T1 through T8 execution and validation passed.
- Current version is recognized as V0.1 Release Candidate（发布候选）.
- Core v0 architecture, MCP Tool Contract（MCP 工具契约）, and boundaries remain unchanged.

Related ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`

## Goal

Create `mcp-ess-proposal` as an independent open-source MCP Server（独立开源 MCP 服务） focused on Tool / Data / Integration / Deterministic Calculation（工具 / 数据 / 集成 / 确定性计算）, migrated from the usable parts of `private-source-tool` without carrying the private platform brand, Lead（线索）, CRM, or the private platform database writes into Core（核心）.

## Router Output

Workflow: PLAN

Reason:

- ADR-0001 is Accepted（已接受）.
- Business scope is clear enough from the current user requirements.
- The work spans project scaffold, MCP tool contracts, deterministic calculation, data fixtures, configuration, tests, and documentation.
- Schema / Contract（结构 / 契约）, external provider risk, sensitive configuration, and validation planning are involved.
- Direct IMPL would be high risk.

Known:

- `mcp-ess-proposal` owns MCP Server / Tool / Data / Integration / Deterministic Calculation.
- `partner-plugin-project` drift is recorded but not refactored in this phase.
- the private platform brand, Lead, CRM, and the private platform database writes are excluded from open-source Core.
- Configuration drift around a provider credential must be fixed in migration scope.

Unknown:

- Final package implementation details may adjust to the selected MCP Python API after scaffold inspection.
- OCR / LLM is intentionally deferred out of Core v0 unless a later accepted PLAN revision adds an optional adapter task.

Required Context:

- Accepted ADR-0001.
- `private-source-tool` source path: `<PRIVATE_SOURCE_ROOT>`.
- `partner-plugin-project` comparison path: `<PARTNER_PROJECT_ROOT>`.
- Harness rules: API Contract Rules（API 契约规则） and Security Rules（安全规则）.

## Preconditions

- Requirements are clear: refactor toward open-source MCP runtime, not a full one-pass rewrite.
- Architecture boundary is accepted in ADR-0001.
- Data Owner（数据归属） for Core is open-source sample / deterministic calculation data only.
- the private platform private ownership remains outside Core.
- No business code will be modified during PLAN.
- Current `private-source-tool` worktree has existing user changes; IMPL must preserve them and avoid destructive operations.

## Selected Context

- `AGENTS.md`
- `.ai/workflows/router.md`
- `.ai/workflows/plan.md`
- `.ai/rules/api-contract.md`
- `.ai/rules/security.md`
- `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`
- `private-source-tool`: `README.md`, `docs/mcp.md`, `mcp_server.py`, `service.py`, `models.py`, the private lead repository, the private audit logger, the private OCR module, `api.py`, `main.py`, `.env.example`, `.gitignore`, `pyproject.toml`, `requirements.txt`, selected `data/`, and tests.
- `partner-plugin-project`: top-level README, package metadata, the partner platform patch, and tool-registration evidence only.

## PLAN Decisions

- Core v0 includes deterministic proposal generation from structured inputs.
- Core v0 excludes OCR / LLM bill-image extraction. Reason（原因）: OCR / LLM introduces provider credentials, prompt ownership, network calls, and prompt logic that are not necessary to validate the Core deterministic MCP contract.
- Core v0 excludes `submit_consultation_lead`, Lead persistence, CRM routing, and the private platform database writes.
- Core v0 excludes public `hello`. Diagnostic validation should be implemented through tests or a non-domain smoke path, not a public MCP business tool.
- Core v0 must fix configuration drift by not documenting provider keys that Core does not use. If a later optional OCR adapter is approved, a provider credential must be documented consistently with code.
- `partner-plugin-project` remains unchanged in this phase. Its runtime overlap is tracked as existing Architecture Drift（既有架构漂移） only.

## Change Set

New files expected in `mcp-ess-proposal`:

- Project scaffold and package metadata for `mcp-ess-proposal`.
- MCP server entrypoint.
- Deterministic proposal domain model and calculator.
- Neutral sample data fixtures.
- Explicit MCP tool contract documentation.
- Secret-safe `.env.example` if runtime configuration is needed.
- Unit and contract tests.
- README / CONTRIBUTING / documentation updates.
- Project Context（项目上下文） and runtime recovery state if required by Harness.

Excluded from Core:

- `prompt/system.md` and partner platform prompt templates.
- `.env` or any secret-bearing config.
- the private platform company contact config.
- the private lead repository persistence behavior.
- the private platform database / CRM write path.
- Runtime private lead persistence and private audit storage.
- `uploads/`, `.venv/`, `__pycache__/`, screenshots, `.DS_Store`.

## Ordered Tasks

### Task 1: Establish MCP Tool Contract

Goal:
Define the public Core tool surface before moving code.

Target:
`docs/contracts/mcp-tools.md`, `docs/project/PROJECT.md` if created.

Dependencies:
None.

Changes:

- Document `generate_ess_proposal` as the only Core v0 public MCP tool.
- Define input schema, output schema, error behavior, side-effect semantics, and compatibility notes.
- Explicitly mark `submit_consultation_lead`, `generate_ess_proposal_from_bill`, and `hello` as excluded from Core v0.
- Record OCR / LLM extraction as future optional adapter scope, not Core v0.

Validation:

- Code-path Review（代码路径审查） against `private-source-tool/mcp_server.py`.
- Contract checklist against `.ai/rules/api-contract.md`.

### Task 2: Create Open-Source Project Scaffold

Goal:
Create a minimal Python MCP project structure without importing private coupling.

Target:
`pyproject.toml`, package directory, `.gitignore`, `.env.example`, README skeleton.

Dependencies:
Task 1.

Changes:

- Set package name to `mcp-ess-proposal`.
- Include only dependencies required by deterministic MCP Core.
- Exclude `psycopg`, FastAPI, UploadFile handling, DashScope / DeepSeek provider usage, and OCR dependencies from Core v0 unless Task 1 is revised.
- Ensure `.gitignore` excludes `.env*` except `.env.example`, runtime output, cache, virtualenv, and uploads.

Validation:

- `python -m compileall` or equivalent import check.
- Package metadata review.
- Secret-safe config review.

### Task 3: Extract Deterministic Calculation Core

Goal:
Move deterministic proposal logic into neutral, testable modules.

Target:
Calculator, domain models, data loader.

Dependencies:
Task 2.

Changes:

- Adapt `ProposalInput` into explicit structured models.
- Extract tariff estimation, PV sizing, storage sizing, financial calculation, and disclaimer handling from `service.py`.
- Remove the private platform-branded summary text and company contact output from Core.
- Return structured output suitable for MCP consumers.

Validation:

- Unit tests for monthly bill input, monthly kWh input, residential tariff, budget cap, backup/storage request, and missing required consumption data.
- Failure-path tests for invalid input.

### Task 4: Replace Private Data With Neutral Fixtures

Goal:
Provide open-source sample data without private brand coupling.

Target:
`data/` fixtures and data documentation.

Dependencies:
Task 3.

Changes:

- Create neutral tariff and product sample data with clear disclaimer.
- Do not import the private platform product URLs, the private platform contact data, CRM assumptions, or private platform names into Core.
- Keep data shape stable for deterministic calculator tests.

Validation:

- JSON schema or parser validation.
- Unit tests proving sample data loads.
- Manual review for the private platform strings.

### Task 5: Implement MCP Server Adapter

Goal:
Expose the deterministic Core through MCP without side effects.

Target:
MCP server entrypoint and tool registration.

Dependencies:
Tasks 1, 2, 3, 4.

Changes:

- Register only the accepted Core v0 tool.
- Ensure tool execution performs no file writes, DB writes, CRM writes, uploads, or network calls.
- Define predictable validation errors and internal errors.

Validation:

- MCP server smoke test.
- Tool contract test for accepted input/output.
- Negative test proving excluded tools are not registered.
- Side-effect review: no append writes, DB connector, upload write, provider client, or prompt file dependency in Core path.

### Task 6: Configuration Drift Cleanup

Goal:
Make configuration documentation match actual Core runtime behavior.

Target:
`.env.example`, README config section, optional adapter notes.

Dependencies:
Tasks 1 and 5.

Changes:

- Remove internal database configuration, `DATABASE_URL`, a provider credential, and a provider credential from Core config unless used by accepted Core code.
- If optional OCR / LLM adapter is later added, document a provider credential and any DeepSeek key consistently with code.
- State that no secret-bearing `.env` is committed.

Validation:

- Secret-safe grep for forbidden variable names in Core docs/code.
- Confirm no `.env` is tracked.

### Task 7: Documentation And Harness State Sync

Goal:
Make docs match the new project boundary and Harness recovery model.

Target:
README, `docs/project/`, handoff, Harness gap log, optional execution state.

Dependencies:
Tasks 1 through 6.

Changes:

- Document project purpose, non-goals, tool contract, data assumptions, and validation commands.
- Keep Harness gaps as observations only; do not modify Harness Source（Harness 源码）.
- Record `partner-plugin-project` runtime overlap as existing drift outside this phase.

Validation:

- Documentation review against ADR-0001.
- Scope Drift（范围漂移） review.

### Task 8: Final Validation And Diff Review

Goal:
Verify the first migration slice is complete and safe.

Target:
Whole `mcp-ess-proposal` repository.

Dependencies:
Tasks 1 through 7.

Changes:

- No new feature changes; validation only.

Validation:

- Format.
- Typecheck or static import check.
- Unit tests.
- MCP contract tests.
- Build/package check if configured.
- Secret scan focused on `.env`, provider keys, the private platform database URLs, the private platform brand leakage, CRM/Lead paths.
- Final diff review for Scope Drift.

## Validation Plan

- Executed during PLAN: Code-path Review（代码路径审查） only.
- Required before any task becomes COMPLETE（完成）:
  - Unit tests for deterministic calculation.
  - Contract tests for MCP input/output and excluded tools.
  - Secret-safe checks for `.env`, the private platform database, CRM, the private platform strings, and provider keys.
  - Documentation review against ADR-0001.
  - Final diff review.

## Risks

- Existing `private-source-tool` has dirty changes. IMPL must not overwrite them.
- If Core v0 imports existing README or config blindly, the private platform coupling will leak into open source.
- If OCR / LLM is pulled into Core early, prompt ownership and provider secret handling become blockers.
- If tool contracts remain implicit, downstream MCP consumers may depend on unstable signatures.
- If `partner-plugin-project` drift is treated as the target boundary, responsibility duplication will persist.

## Documentation Impact

- `docs/contracts/mcp-tools.md` required.
- `docs/project/PROJECT.md` required or runtime state must explicitly explain why Project Context is unavailable.
- README must describe Core scope and excluded private integrations.
- Handoff must be updated after each completed task.
- `docs/harness/HARNESS-GAPS.md` remains observation-only.

## Ready To Enter IMPL

Yes.

Reason（原因）: PLAN-0001 was approved by Human Approval（人工审核）. Task 1 is the first implementation task.
