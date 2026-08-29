# ADR-0001: Open Source MCP ESS Proposal Boundaries

Status: Accepted

Date: 2026-08-29

## Context

The requested goal is to refactor the current `private-source-tool` into an open source project named `mcp-ess-proposal`, while using this work to validate whether `ai-codeops-harness` can govern a real MCP project.

The explicit user requirements are:

- Check Private Platform Coupling（私有平台耦合）.
- Check Sensitive Configuration（敏感配置）.
- Check MCP Tool Boundary（MCP 工具边界）.
- Check overlap with `partner-plugin-project`.
- Keep `partner-plugin-project` focused on Skill / Knowledge / Workflow（技能 / 知识 / 工作流）.
- Keep `mcp-ess-proposal` focused on MCP Server / Tool / Data / Integration（MCP 服务 / 工具 / 数据 / 集成）.
- Record Harness Gaps（治理缺口） without modifying Harness Source（Harness 源码）.
- Do not perform the whole refactor in one pass.
- Do not copy Skill / Prompt logic from `partner-plugin-project`.
- Do not commit architecture-changing implementation before Harness confirmation.

## Acceptance

Human Approval（人工审核） was provided on 2026-08-29.

Accepted supplemental decisions:

- `mcp-ess-proposal` is an independent MCP Server（独立 MCP 服务） focused on Tool / Data / Integration / Deterministic Calculation（工具 / 数据 / 集成 / 确定性计算）.
- Existing runtime / OCR / calculation logic in `partner-plugin-project` is not refactored in this phase. It is recorded as existing Architecture Drift（既有架构漂移） and must not be used as the new project boundary reference.
- the private platform brand, Lead（线索）, CRM, and the private platform database writes from `private-source-tool` must not enter the open-source Core（开源核心）.
- Whether OCR / LLM belongs in MCP Core is not predetermined. Tool Contract（工具契约） and PLAN must decide it based on necessity.
- `hello` is a diagnostic Tool（诊断工具） candidate. PLAN must evaluate whether it remains a public interface.
- Fixing configuration drift between a provider credential usage and configuration examples is mandatory migration scope.

Router Output（路由输出）:

- Workflow: ADR
- Reason: The task is not a localized implementation change. It changes System Boundary（系统边界）, Tool Boundary（工具边界）, Data Ownership（数据归属）, Integration Ownership（集成归属）, and open-source security posture.
- Known: The intended responsibility split is clear at a high level: `partner-plugin-project` owns Skill / Knowledge / Workflow, while `mcp-ess-proposal` owns MCP Server / Tool / Data / Integration.
- Unknown: Implementation task order, exact MCP tool contracts, and whether OCR / LLM belongs in Core remain for PLAN.
- Required Context: PLAN must use this Accepted ADR, the inspected `private-source-tool` source, the current `partner-plugin-project` drift evidence, and secret-safe configuration policy.

## Current Reality

Current Reality（当前事实） checked in this repository:

- The git repository has no commits.
- `git ls-files` returns no tracked files.
- The working tree currently contains only `AGENTS.md` and the installed `.ai/` Harness files.
- `.ai/state/execution-state.yaml` is missing.
- `docs/handoff/HANDOFF-current.md` was missing before this ADR-stage recovery documentation was created.
- `docs/project/` is missing, so Project Context（项目上下文） cannot be resolved from runtime state.
- No application source, MCP server code, tool schema, contracts, `.env.example`, package manifest, README, PRD, ADR, PLAN, or tests are present.
- The source project was later provided at `<PRIVATE_SOURCE_ROOT>`.
- The comparison project was found at `<PARTNER_PROJECT_ROOT>`.

Current Reality（当前事实） checked in `private-source-tool`:

- The source is inside git repository `<PRIVATE_SOURCE_ROOT>`.
- The source worktree has pre-existing modifications in `.env.example`, `.gitignore`, the private lead repository, `pyproject.toml`, and `requirements.txt`; these were inspected but not modified.
- The project package name, MCP server name, README, API title, docs, license copyright, config, product catalog URLs, and summary text still use the private platform naming.
- `mcp_server.py` registers four MCP tools: `hello`, `generate_ess_proposal`, `submit_consultation_lead`, and `generate_ess_proposal_from_bill`.
- `docs/mcp.md` lists only three tools and omits `generate_ess_proposal_from_bill`.
- `submit_consultation_lead` has side effects: it requires `consent=true`, writes private lead persistence, writes audit events to private audit storage, and, when internal database configuration is configured, writes to PostgreSQL an internal lead table.
- `.env` exists in the source directory but was not read. `.gitignore` excludes `.env`, `.env.*`, runtime lead/audit JSONL files, uploads, virtual environments, and cache files. `git ls-files` confirms `.env.example` is tracked and `.env` / runtime JSONL files are not tracked.
- `.env.example` documents a provider credential and optional internal database configuration. the private OCR module actually reads a provider credential, creating a documented configuration mismatch.
- the private OCR module sends local bill images as base64 `data:` image URLs to DashScope-compatible Qwen-VL and returns model-derived structured data.
- `service.py` performs deterministic proposal calculations from local JSON data and writes the private platform-branded summary text.
- `prompt/system.md` contains the private platform-specific proposal prompt logic. This content is outside the proposed MCP runtime boundary and must not be copied from or into `partner-plugin-project` as Skill / Prompt ownership.
- `api.py` and `main.py` are currently inconsistent with `models.py` and `service.py`: they reference fields/classes such as `ProposalOutput`, `bill_images`, `site_images`, and `target_payback_years` that are not defined on the dataclass model, and they `await generate_proposal` even though `service.generate_proposal` is synchronous.
- Tests are present but empty: `test/test_mcp_server.py` and `test_proposal.py` contain no executable assertions.

Current Reality（当前事实） checked in `partner-plugin-project`:

- The project is a the partner platform plugin named `partner-plugin-project`.
- It registers a `generate_ess_proposal` tool through `@deepseek-ai/partner-plugin-tools`.
- It includes prompt templates, local data assumptions, OCR fallback logic, Qwen-VL / DeepSeek integration, deterministic proposal calculation, and tool output rendering.
- Its README positions it as a partner platform plugin, not merely a Skill / Knowledge / Workflow document set.
- Therefore the user-stated target boundary differs from current reality: today `partner-plugin-project` also owns runtime Tool / Data / Integration behavior that should belong to `mcp-ess-proposal` if the target boundary is accepted.

Validation Evidence（验证证据）:

- Code-path Review（代码路径审查）: Repository structure, source paths, git metadata, key source files, MCP tool registration, config references, data writes, and `partner-plugin-project` top-level implementation were inspected.
- Executed Test（已执行测试）: None. ADR Current Reality used code-path review only.
- NOT RUN（未执行）: Full secret scan, MCP contract tests, build, typecheck, integration tests.

## Drift Detection

Architecture Drift（架构漂移）:

- The desired target boundary says `partner-plugin-project` should own Skill / Knowledge / Workflow only.
- Current `partner-plugin-project` also owns partner platform tool registration, OCR / LLM integration, deterministic proposal calculation, data assumptions, and runtime configuration.
- The desired target boundary says `mcp-ess-proposal` should own MCP Server / Tool / Data / Integration.
- Current `private-source-tool` is closer to that boundary, but it remains the private platform branded and contains prompt logic, the private platform database integration, local runtime writes, and inconsistent REST / CLI surfaces.

This is Architecture Drift relative to the requested target state, not an implementation bug.

Runtime State Drift（运行时状态漂移） / Bootstrap Gap（启动缺口） exists:

- `AGENTS.md` requires `.ai/state/execution-state.yaml` and `docs/handoff/HANDOFF-current.md` during session bootstrap.
- Both were absent at the start of this session.
- Because there is no runtime state, there is no active PRD / ADR / PLAN reference to load.

This repository is now ready for Router re-entry. It is not ready for IMPL until PLAN is complete.

## Decision Problem

Define the open-source target boundary before any refactor:

What must `mcp-ess-proposal` own, what must remain outside it, and what evidence is required before it can be planned and implemented safely?

## Options

### Option A: Merge Skill / Knowledge / Workflow into `mcp-ess-proposal`

Benefits:

- One repository would contain all project guidance and runtime code.

Costs:

- Duplicates `partner-plugin-project` responsibilities.
- Blurs MCP runtime contracts with AI workflow assets.
- Encourages copying Skill / Prompt logic, which the user explicitly forbids.

Security:

- Higher risk of accidentally mixing workflow examples, internal prompts, and runtime configuration.

Result: Rejected.

### Option B: Keep `mcp-ess-proposal` as the MCP runtime and integration boundary, with `partner-plugin-project` as a consumer / workflow layer

Benefits:

- Clear owner for MCP Server（MCP 服务）, MCP Tool Contracts（MCP 工具契约）, Data Access（数据访问）, Provider Adapters（供应商适配器）, and Integration Configuration（集成配置）.
- Allows `partner-plugin-project` to remain focused on Skill / Knowledge / Workflow.
- Makes sensitive configuration and public tool contracts easier to audit for open source release.
- Matches the Harness API Contract Rules for MCP / Tool interfaces.
- Creates a migration path where duplicated partner platform runtime behavior can call or reference stable MCP tools instead of owning duplicate calculation and integration logic.

Costs:

- Requires explicit contract and boundary documentation before implementation.
- Requires migration planning for both `private-source-tool` and the overlapping runtime behavior currently inside `partner-plugin-project`.

Security:

- Best fit for secret minimization and public repository review.

Result: Selected and Accepted.

### Option C: Keep the private platform-specific behavior in the open-source MCP project

Benefits:

- Fastest if the existing project is strongly product-specific.

Costs:

- Keeps vendor or customer coupling in a public runtime project.
- Weakens open-source reusability.
- Makes sensitive configuration review harder.

Security:

- Higher risk of exposing proprietary naming, internal endpoints, or operational assumptions.

Result: Rejected as a target state, but real coupling points must be inspected before migration tasks are written.

### Option D: Create a generic MCP shell now and retrofit code later

Benefits:

- Allows immediate repository scaffolding.

Costs:

- Risks inventing architecture before checking the real implementation.
- Could hide important the private platform coupling decisions.

Security:

- May miss actual secret and data-flow risks.

Result: Rejected for this ADR stage.

## Decision

`mcp-ess-proposal` should be the open-source MCP runtime project. It owns MCP Server（MCP 服务）, Tool Contracts（工具契约）, Data Contracts（数据契约）, Provider / Integration Adapters（供应商 / 集成适配器）, runtime configuration names, validation, and tests.

`partner-plugin-project` remains outside this repository and should own Skill / Knowledge / Workflow（技能 / 知识 / 工作流） assets and any partner-platform-specific adapter behavior. `mcp-ess-proposal` must not copy Prompt（提示词） or Skill（技能） logic from `partner-plugin-project`.

Because Current Reality shows `partner-plugin-project` currently owns runtime Tool / Data / Integration behavior too, this is recorded as existing Architecture Drift（既有架构漂移）. The current drift is not refactored in this phase and must not be used as the boundary reference for `mcp-ess-proposal`.

the private platform brand, Lead capture, CRM routing, and the private platform database writes are excluded from the open-source Core. They may only appear later as optional private adapters if a future ADR accepts that boundary.

OCR / LLM integration is intentionally undecided at the ADR level. PLAN must evaluate whether image-based bill extraction is necessary for the first open-source MCP scope, or whether Core should start with deterministic calculation from structured inputs.

Before IMPL, PLAN must resolve:

- Whether `submit_consultation_lead` remains in the open-source MCP package, becomes optional, or moves behind an adapter.
- Whether the private platform-branded product catalogs remain as sample data, are replaced by neutral fixtures, or move to a private integration package.
- Whether `prompt/system.md` should be excluded from `mcp-ess-proposal` or replaced by tool contract documentation only.
- Whether REST API and CLI surfaces remain in scope for the MCP open-source project.
- Whether `hello` remains a public diagnostic tool.
- How to fix the a provider credential / configuration sample drift.

## Consequences

Positive（正向结果）:

- Establishes a clear open-source boundary before implementation.
- Prevents uncontrolled copying from `partner-plugin-project`.
- Gives security review a concrete surface: MCP tools, data access, integrations, and configuration.

Negative（代价）:

- PLAN is now allowed and required before implementation.
- The migration must account for existing dirty source changes in `private-source-tool`.

Risks（风险）:

- If the private platform database integration remains enabled by default, the open-source MCP package may leak private platform assumptions.
- If prompt files are copied across repositories, the intended `partner-plugin-project` responsibility boundary will be violated.
- If MCP tool schemas are left implicit, tool consumers will depend on unstable Python signatures and natural-language descriptions.
- Missing runtime state makes cross-session recovery weaker.

Follow-up（后续）:

- Enter PLAN with scoped migration tasks that separate runtime MCP concerns from prompt / workflow concerns.
- Add explicit MCP tool contract documentation before changing tool signatures.
- Add a secret-safe open-source configuration policy before importing `.env.example` or provider integration code.

## Related ADR

Supersedes: None.

Related:

- `AGENTS.md`
- `.ai/workflows/router.md`
- `.ai/workflows/adr.md`
- `.ai/rules/api-contract.md`
- `.ai/rules/security.md`
- `<PRIVATE_SOURCE_ROOT>`
- `<PARTNER_PROJECT_ROOT>`

## Documentation Impact

Required during PLAN / IMPL（PLAN / 实施期间必须补齐）:

- Project Context（项目上下文） under `docs/project/`.
- Runtime recovery state under `.ai/state/execution-state.yaml`.
- A current handoff under `docs/handoff/HANDOFF-current.md`.
- Open-source README describing project ownership and non-goals.
- MCP tool contract documentation.
- Configuration documentation with secret-safe examples.
- Migration note for `partner-plugin-project` runtime overlap.

## Ready To Enter PLAN

Yes.

Reason（原因）: Current Reality has been checked and Human Approval（人工审核） accepted the boundary with supplemental decisions. Router must re-enter and select PLAN before IMPL.
