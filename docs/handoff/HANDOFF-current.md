# Handoff Current

Date: 2026-08-29

## Current Stage

Workflow: IMPL

Status（状态）: **Blocked External Auth（外部认证阻塞） / CI Observation Blocked（CI 观察阻塞）**. MCP Tool Contract is Core v0.2, dependency alignment to MCP SDK 2.1.1 is locally validated, and Release Safety Gate passes. Release Candidate Ready（发布候选就绪） is not restored because true Claude Host E2E could not run without Claude authentication and GitHub CI status is not observable from this unauthenticated session.

Approval Record（审批记录）:

- Approved by（批准人）: human project owner, during the Cross-Agent Recovery（跨智能体恢复） session on 2026-08-29.
- Approved scope（批准范围）: PLAN-0002 Task 1 through Task 5, executed consecutively.
- MIT `LICENSE` uses Neutral Personal Copyright Text（中性个人版权文本）; no the private platform corporate entity.
- Minimal GitHub CI validates Python 3.11 only; no version matrix expansion.
- Two Cross-Agent Recovery findings are appended to `docs/harness/HARNESS-GAPS.md` as observation-only.
- `ai-codeops-harness` Source（Harness 源码） must not be modified.
- Stop conditions（停止条件）: Secret / Private Data Review anomaly, Drift（漂移）, Validation Failure（验证失败）, Security Boundary Change（安全边界变更）, Release Approval（发布审批）.

## Router Result

Router first selected ADR because the requested refactor changes System Boundary（系统边界）, MCP Tool Boundary（MCP 工具边界）, Data Ownership（数据归属）, Integration Ownership（集成归属）, and open-source security posture.

After ADR-0001 was Accepted（已接受）, Router re-entered and selected PLAN because the work spans multiple files, MCP contracts, data fixtures, configuration, security checks, and validation planning.

After PLAN-0001 was Approved（已批准）, IMPL executed Task 1 through Task 8 in separate turns.

After PLAN-0001 Human Final Review passed, Router selected PLAN for Release Preparation because the next phase spans license, GitHub CI, README open-source readiness, final secret/private-data review, and Harness recovery state.

After PLAN-0002 received Human Approval（人工审核） on 2026-08-29, Router re-entered and selected IMPL for the approved Release Preparation task sequence.

After PLAN-0002-T4 found private internal detail in Governance Artifacts（治理产物）, Router re-entered and selected ADR. ADR-0001 scoped its boundary to Source Code（源代码） only and never decided the publication boundary for Governance Artifacts or the ownership of installer-managed Harness Runtime（Harness 运行时）. That is Architecture Drift（架构漂移）, so IMPL escalated instead of editing the Accepted ADR. `docs/adr/ADR-0002-open-source-governance-artifact-boundary.md` was produced as an Amendment Proposal（修订提案）.

## Current Reality

- The `mcp-ess-proposal` repository has an initial pushed baseline at `34a179f01fbfa825a78125e8a24e6ba7b7de9ca1`; the first GitHub CI run failed on MCP SDK dependency drift.
- Current Git reality from resume: branch `master`, HEAD `bb3880df60631a7e1f8d18dcd5cfea1768409dab`, remote `origin/master` at the same commit, clean worktree before state reconciliation.
- Current files include the accepted ADR, approved PLAN, accepted MCP Tool Contract, project scaffold, deterministic Core, neutral fixtures, stdio MCP Server Adapter, tests, and Harness recovery artifacts created during this governed migration.
- `.ai/state/execution-state.yaml`, `docs/handoff/HANDOFF-current.md`, and `docs/project/` were absent at session start and now exist as Harness recovery / project context artifacts.
- `private-source-tool` source path is `<PRIVATE_SOURCE_ROOT>`.
- `partner-plugin-project` comparison path is `<PARTNER_PROJECT_ROOT>`.
- `private-source-tool` is the private platform-branded and contains MCP tools, local data, prompt logic, provider calls, REST / CLI surfaces, and lead persistence.
- `partner-plugin-project` is a the partner platform plugin but also contains runtime tool registration, prompts, data assumptions, OCR / LLM integration, and deterministic calculation logic.

## Created Artifacts

- `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`
- `docs/plan/PLAN-0001-mcp-ess-open-source-migration.md`
- `docs/plan/PLAN-0002-release-preparation.md`
- `docs/contracts/mcp-tools.md`
- `docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md`
- `docs/project/PROJECT.md`
- `.ai/state/execution-state.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T1.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T2.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T3.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T4.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T5.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T6.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T7.yaml`
- `.ai/state/checkpoints/tasks/PLAN-0001-T8.yaml`
- `docs/harness/HARNESS-GAPS.md`
- `docs/handoff/HANDOFF-current.md`
- `pyproject.toml`
- `README.md`
- `.gitignore`
- `.env.example`
- `src/mcp_ess_proposal/__init__.py`
- `src/mcp_ess_proposal/__main__.py`
- `src/mcp_ess_proposal/data.py`
- `src/mcp_ess_proposal/fixtures/calculation-defaults.json`
- `src/mcp_ess_proposal/fixtures/sample-products.json`
- `src/mcp_ess_proposal/models.py`
- `src/mcp_ess_proposal/calculator.py`
- `src/mcp_ess_proposal/server.py`
- `tests/.gitkeep`
- `tests/test_calculator.py`
- `tests/test_server.py`
- `tests/test_stdio_runtime.py`
- `tests/test_configuration.py`
- `docs/data/fixtures.md`
- `docs/project/SYSTEM-MAP.md`

## Decision State

ADR-0001 is Accepted（已接受）.

Accepted boundary:

- `mcp-ess-proposal` owns MCP Server / Tool / Data / Integration.
- `partner-plugin-project` owns Skill / Knowledge / Workflow and partner-platform-specific adapter behavior.
- `mcp-ess-proposal` must not copy Skill / Prompt logic from `partner-plugin-project`.
- the private platform brand, Lead, CRM, and the private platform database writes must not enter open-source Core.
- OCR / LLM Core membership is deferred to Tool Contract / PLAN.
- a provider credential configuration drift was planned for migration and resolved for Core v0 in Task 6 by keeping Core configuration zero-secret.

## Task State

- COMPLETE（已完成）: PLAN-0001 T1-T8; PLAN-0002 T1-T4; PLAN-0003 T1-T10.
- SUPERSEDED（已被取代）: PLAN-0002-T5, absorbed by PLAN-0003-T10.
- BLOCKED（阻塞）: true Claude Host E2E cannot run because local Claude Code is not authenticated.
- READY / INTERRUPTED / ESCALATED: none.
- Decisions（决策）: ADR-0002 Accepted with D1-D4; CONTRACT AMENDMENT-0001 and AMENDMENT-0002 Accepted for Core v0.2.

## Release Readiness（发布就绪）

| Item | Result |
| --- | --- |
| Contract version | Core v0.2, implemented and schema-verified at runtime |
| Tests | 58 passed under Python 3.11 + MCP 2.1.1 |
| Schema fidelity | PASS; runtime discovery adds only approved root `type: object` normalization |
| Claude Code Host E2E | BLOCKED; local Claude auth is absent (`loggedIn: false`, API 403 before MCP calls) |
| Release Safety Gate | PASS, 0 findings, 3 allowlisted, 0 unscannable binaries |
| CI | fix pushed; status not observable here because private GitHub Actions requires authenticated access |
| Public baseline | 47 files |
| Package build | wheel/sdist built and fresh wheel install smoke passed under Python 3.11 + MCP 2.1.1 |

Excluded from the public baseline per ADR-0002 D4: `AGENTS.md`, `.ai/rules/**`, `.ai/roles/**`, `.ai/workflows/**`, `.ai/VERSION`. Also excluded: `imgs/`, unreferenced personal session screenshots that a text validator cannot scan.

Not authorized and not performed（未授权且未执行）: git tag, GitHub Release, package registry publish, public announcement.

## MCP Learning Points

Task 1 learning:

- MCP Protocol（MCP 协议）: the tool contract must be independent of transport and client session details.
- Tool Contract（工具契约）: side effects must be explicit; Core v0 makes `generate_ess_proposal` side-effect free.
- Transport（传输）: stdio and streamable HTTP can be implementation choices later, but must not change input/output/error semantics.
- Client（客户端）: clients should rely on structured output, not natural-language rendering or diagnostic tools.
- Server（服务端）: Core server boundaries exclude Lead, CRM, the private platform database writes, provider calls, OCR/LLM, and prompt loading.

Task 2 learning:

- MCP Protocol（MCP 协议）: project packaging should not imply extra protocol methods before the contract-backed tool exists.
- Tool Contract（工具契约）: scaffold metadata and README must point to the accepted contract instead of restating divergent schemas.
- Transport（传输）: no stdio or HTTP transport behavior was implemented in the scaffold; transport remains a later server-adapter concern.
- Client（客户端）: README exposed only the accepted contract status, so clients were not encouraged to call excluded tools.
- Server（服务端）: dependency selection is part of the server boundary; Core scaffold excludes provider, DB, upload, OCR, LLM, and CRM dependencies.

Task 3 learning:

- MCP Protocol（MCP 协议）: contract-shaped domain output can be implemented before MCP transport wiring, keeping protocol concerns separate from calculation correctness.
- Tool Contract（工具契约）: rejecting unsupported fields such as image inputs protects Core from accidental OCR / upload scope expansion.
- Transport（传输）: deterministic Core takes plain structured data and has no dependency on stdio, HTTP, file paths, or session state.
- Client（客户端）: clients receive stable structured errors for validation failures instead of localized prose from the old implementation.
- Server（服务端）: side-effect-free calculation means no IDs, audit files, DB writes, provider calls, or prompt loading in the Core path.

Task 4 learning:

- MCP Protocol（MCP 协议）: data fixtures are server-owned implementation resources, not client-provided protocol state.
- Tool Contract（工具契约）: fixture shape must support the accepted output schema without adding new public tool fields.
- Transport（传输）: package-resource fixture loading remains independent of stdio, HTTP, auth, and session transport.
- Client（客户端）: clients should not supply tariff files, local product paths, or private configuration in Core v0.
- Server（服务端）: neutral package data prevents private brand, provider, database, OCR/LLM, prompt, lead, CRM, and upload coupling from entering Core.

Task 5 learning:

- MCP Protocol（MCP 协议）: low-level `Server` registration can preserve accepted discovery schemas when higher-level helpers cannot express strict cross-field constraints.
- Tool Contract（工具契约）: runtime discovery now exposes one tool and uses the accepted `anyOf` / `additionalProperties: false` input schema; SDK validation rejects missing consumption input before Core execution.
- Transport（传输）: Core v0 uses stdio only through `run_stdio`; remote HTTP, authentication, providers, and private adapters remain outside this task.
- Client（客户端）: a real MCP `ClientSession` can initialize, list `generate_ess_proposal`, call it, and receive `structuredContent` plus JSON text content.
- Server（服务端）: the handler remains a thin adapter: MCP arguments enter the handler, Core `generate_ess_proposal` performs calculation, and the server returns contract-shaped output.

Task 6 learning:

- MCP Protocol（MCP 协议）: Core v0 tool semantics are not controlled by environment variables or secret-bearing configuration.
- Tool Contract（工具契约）: `generate_ess_proposal` remains callable from structured input only; provider keys, database URLs, and OCR / LLM settings are not hidden inputs.
- Transport（传输）: stdio startup is explicit in the command path and is not selected through runtime configuration in Core v0.
- Client（客户端）: clients do not need to provision `.env` files or API keys to call the accepted tool.
- Server（服务端）: runtime source has no dotenv loading, provider key reads, database URLs, or private configuration fallback.

Task 7 learning:

- MCP Protocol（MCP 协议）: README and System Map now document the actual Host / Client / stdio / Server / Tool / Core runtime path without adding protocol behavior.
- Tool Contract（工具契约）: documentation links to the accepted contract and does not redefine schema, fields, or tool inventory.
- Transport（传输）: stdio remains the only documented Core v0 transport; Remote HTTP（远程 HTTP） and Authentication（鉴权） remain outside current scope.
- Client（客户端）: third-party clients can identify install, startup, configuration, and sample argument requirements from README without needing private project context.
- Server（服务端）: Project Context records that source and comparison repositories are evidence only, not runtime dependencies.

Task 8 learning:

- MCP Protocol（MCP 协议）: final runtime validation should include both source checkout and installed-package stdio ClientSession smoke tests.
- Tool Contract（工具契约）: runtime discovery confirmed exactly one public Tool（工具）, `generate_ess_proposal`, with strict input schema and ok/error output schema.
- Transport（传输）: stdio is release-validated for Core v0; Remote HTTP（远程 HTTP） and Authentication（鉴权） remain explicitly untested and out of scope.
- Client（客户端）: third-party clients can install the package, connect over stdio, list the tool, and call it without environment secrets.
- Server（服务端）: package artifacts include neutral fixtures and entry point metadata; Core remains deterministic, side-effect free, zero-secret, and private-coupling-free.

## Remaining Harness Gaps

- `docs/harness/PROJECT-CONTEXT-CONTRACT.md` is referenced by AGENTS.md but is absent in this repository.
- MCP-specific governance gaps remain recorded in `docs/harness/HARNESS-GAPS.md`.
- Documentation Language Policy（文档语言策略） is recorded as a Harness improvement gap and was not applied as a broad translation task.

## Secret And Private-Data Review Result（安全与私有数据审查结果）

Executed for PLAN-0002-T4 on 2026-08-29 before any `git add`.

PASS（通过）:

- No secret value exists anywhere in the baseline scope: no API key, token, credential, private key block, connection string, or high-entropy literal.
- `.env` and `.env.local` are ignored, `.env.example` is un-ignored and declares no variables, and no `.env` file exists in this repository.
- Runtime source, fixtures, packaging metadata, `LICENSE`, CI workflow, and README are free of private coupling.
- `tests/test_configuration.py` splits forbidden names deliberately so the literals never appear; it is a correct negative test.
- The private source project was not modified by this phase. Its uncommitted changes date to 2026-08-15 and 2026-08-18.

FAIL（未通过）:

- Governance documents would publish private internal detail at the first tracked baseline: 16 occurrences of absolute developer filesystem paths disclosing the developer account name and the private platform directory layout, plus private environment variable names, a private database table name, and private runtime file paths recorded as migration evidence.
- These are not secrets. The problem is that publishing the governance record itself was never an accepted decision. ADR-0001 excluded private detail from Core, but said nothing about `docs/` and `.ai/`.

Scan method note（扫描方法说明）: the first scan pass produced a false clean result. Under an empty `LANG`, a multibyte grep pattern makes BSD grep exit 2, and an `|| echo clean` idiom reports that error as a pass. Scans were re-run under a UTF-8 locale with explicit exit-code classification.

## Architecture Drift Decision（架构漂移决策）

The project owner selected sanitization over exclusion on 2026-08-29:

- Governance Artifacts stay in the public repository, because ADR / PLAN / Contract / Project / System Map carry real governance value.
- They must pass Open-Source Sanitization（开源脱敏） first.
- Source Code（源代码） and Governance Artifact（治理产物） are both in Release Review（发布审查） scope.
- The Accepted ADR must not be edited inside IMPL. Router routes to ADR Amendment（ADR 修订）.
- `.ai/` ownership is deliberately deferred into the same ADR review. This project's MIT `LICENSE` must not be assumed to cover installer-managed Harness Runtime.

`docs/adr/ADR-0002-open-source-governance-artifact-boundary.md` proposes D1 Governance Artifact Boundary, D2 Open-Source Sanitization, D3 Release Safety Gate, and D4 deferred Harness Runtime ownership with a license constraint.

## ADR-0002 Decision Record（决策记录）

Human Decision（人工决策） of 2026-08-29:

- D1 Governance Artifact Boundary: **Accepted（已接受）**.
- D2 Open-Source Sanitization: **Accepted（已接受）**.
- D3 Release Safety Gate: **Accepted（已接受）**, with Deterministic Validator（确定性验证器）, at least PASS / MATCH_FOUND / TOOL_ERROR, and TOOL_ERROR failing closed.
- D4 Harness Runtime Ownership And Licensing: **Unresolved External Dependency（未决外部依赖）**. Not approved and not inferred.

Document status stays `Proposed`（提案中）. The Harness ADR lifecycle defines only Proposed, Accepted, Superseded, and Deprecated. Partially Accepted（部分接受） is not defined, and no per-decision lifecycle exists, so marking the document `Accepted` would falsely assert that D4 was decided.

Standing constraint（常设约束）: this project's MIT `LICENSE` must not be assumed to cover installer-managed artifacts under `.ai/rules`, `.ai/roles`, `.ai/workflows`, `.ai/VERSION`, or root `AGENTS.md`.

D4 evidence gathered（已收集证据）, read-only, 2026-08-29: the Harness Source Repository was located locally. Its LICENSE, manifest, Installer Contract, and Ownership Model were found and answer *who owns which file for update purposes*. No distribution, redistribution, attribution, or consumer-project licensing policy exists anywhere in the Harness documentation, and no policy states whether a consumer project should Git track installer-managed artifacts. D4 remains blocked on exactly that missing policy.

New fact found during the ADR Current Reality check（ADR 现实检查新发现）: `.ai/` is a mixed directory. 18 files under it are installer-managed third-party content, while the 13 files under `.ai/state/**` are project-owned Runtime Facts required for Cross-Agent Recovery. `AGENTS.md` at the repository root is also installer-managed. All 19 installer-managed files match their recorded sha256, so the Harness Source was not modified.

## Contract Drift（契约漂移）

Detected 2026-08-29 by a Claude Code MCP Host End-to-End test against `generate_ess_proposal`, then reproduced deterministically as Executed Test（已执行测试） evidence.

- E1: a user-supplied `tariff_myr_per_kwh` is rejected as an unsupported field; the default resolves to 0.386 MYR/kWh, so every savings and payback figure inherits it.
- E2: supplying both `monthly_kwh` and `monthly_bill_myr` yields a consumption value matching neither input, because the stated consumption selects the tariff tier and is then discarded.
- E3: precedence differs between residential and non-residential customer types. Found while reproducing, not in the original report.
- E4: non-residential bill conversion uses the residential fallback tariff, so the implied bill contradicts the supplied bill. Found while reproducing, not in the original report.
- E5: the financial investment figure is PV-only but carries no scope marker inside `financial`.

Router selected **PLAN**（选定 PLAN）: the accepted contract already permits compatible optional field additions, and no ADR trigger is met, but the semantic precedence change has compatibility impact and needs explicit scope and migration planning.

`docs/contracts/AMENDMENT-0001-generate-ess-proposal-consumption-and-tariff.md` is **Proposed（提案中）**. The Accepted contract was not modified.

Two parameters inside the amendment are deliberately unresolved: the consistency tolerance band, proposed at 10 percent, and whether an out-of-tolerance mismatch returns an error or a warning, with error recommended.

One boundary question is raised for human ruling rather than resolved downstream: whether accepting a scalar tariff parameter crosses the ADR-0001 data-ownership boundary. The amendment assesses that it does not, because server-owned fixtures remain the sole default data source and the client cannot address or replace them. If the reviewer disagrees, the amendment re-routes to ADR.

## Stage 1 Result（第一阶段结果）

Version aligned to 0.2.0, committed, and pushed. First GitHub CI run **FAILED**.

Root cause（根因）: `pyproject.toml` declares `mcp>=2.0.0`, but all local validation ran against mcp **1.27.2**, which does not satisfy that constraint. CI resolved mcp **2.1.1**, where the low-level `Server` API used by the adapter does not exist: `AttributeError: 'Server' object has no attribute 'list_tools'`.

This is **not** a pure CI or environment fault. The declared dependency surface was never validated, and a consumer installing per this metadata would receive a non-functional server. Resolving it requires either narrowing the declared constraint to the validated 1.x line, or migrating the server adapter to the 2.x low-level API and revalidating schema fidelity. Both need a human decision.

No tag, release, or publish was performed.

## Stage 2 Result（第二阶段结果）

Human Decision（人工决策） approved MCP SDK Dependency Alignment and MCP 2.x Output Schema Normalization on 2026-08-29.

Implemented（已实现）:

- `pyproject.toml` now declares `mcp>=2.1,<3`; package version stays `0.2.0`.
- `src/mcp_ess_proposal/server.py` uses MCP 2.x low-level `add_request_handler` for `tools/list` and `tools/call`.
- Runtime discovery uses MCP 2.x `input_schema` / `output_schema` fields.
- Output schema normalization is limited to top-level `type: "object"` over the accepted `oneOf` success/error branches.
- `docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md` records the approved normalization and Contract Fidelity split.

Validation（验证）:

- Python 3.11 clean environment with `mcp 2.1.1`: PASS.
- Package install with dev dependencies: PASS.
- Full tests: PASS, 58 tests.
- Schema semantic-equivalence and payload validation: PASS.
- MCP 2.1.1 `tools/list` / `tools/call` over stdio: PASS.
- Wheel/sdist build: PASS.
- Fresh wheel install smoke with `mcp 2.1.1`: PASS.
- Installed-wheel stdio smoke for `600 kWh + tariff 0.60`: PASS.
- Installed-wheel stdio smoke for inconsistent consumption input: PASS, `INCONSISTENT_CONSUMPTION_INPUT`.
- Release Safety Gate: PASS.

Blocked（阻塞）:

- True Claude Code Host E2E did not execute. `claude auth status` reports `loggedIn: false` and `authMethod: none`; `claude -p` returns API 403 before any MCP tool call. The old MCP 1.27.2 Host E2E is not used as final Release Evidence（发布证据）.

## Next Required Action

The MCP 2.x dependency-alignment fix was committed and pushed to trigger GitHub CI rerun. CI status is not observable here: `gh` is unavailable and unauthenticated GitHub REST returns 404 for the private repository.

Do not restore Release Candidate Ready until GitHub CI passes and true Claude Host E2E is rerun under MCP 2.x with an authenticated Claude host. No git tag, GitHub Release, registry publish, or public announcement is authorized.

## Resume Check 2026-08-29（恢复检查）

Installed Runtime Evidence（已安装运行时证据）: `.ai/VERSION` reports `ai-codeops-harness` version `0.1.0`, installed adapter `codex`, and 19 managed files. Checksum verification during resume checked all 19 managed files with no missing or mismatched file. The active `AGENTS.md`, `.ai/workflows/orchestrator.md`, and `.ai/workflows/impl.md` contain `plan_continuous` rules.

Resume Evidence（恢复证据）: Runtime State（运行状态） resumed from `docs/plan/PLAN-0003-contract-v0-2-implementation.md` and `docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md`. PLAN-0003 T1-T10 are recorded complete, with no READY or INTERRUPTED task. Current external blockers remain Claude Host E2E authentication and private GitHub Actions status observation.

Current validation rerun（当前验证重跑）: MCP SDK in the clean validation env is `2.1.1`; `tests.test_stdio_runtime_v0_2.McpHostRoundTripV02Tests` passed 8 tests; Release Safety Gate passed with 0 findings, 3 allowlisted, and 0 unscannable files.
