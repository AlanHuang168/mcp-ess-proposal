# Harness Gaps For MCP ESS Proposal

Date: 2026-08-29

Scope（范围）: gaps observed while applying the installed `ai-codeops-harness` to the requested `private-source-tool` to `mcp-ess-proposal` open-source refactor.

## Observed Gaps

### GAP-001: Missing Runtime State Handling

Observation（观察）:

- `AGENTS.md` requires `.ai/state/execution-state.yaml` during bootstrap.
- The file is absent in the current repository.
- The Harness explains how to use state when present, but the local project does not include a bootstrap artifact for a new repository with no PRD / ADR / PLAN yet.

Impact（影响）:

- The agent must infer whether this is State Drift（状态漂移）, an uninitialized repository, or a recovery gap.

Needed Governance Support（需要的治理支持）:

- A documented New Project Initialization（新项目初始化） path for creating minimal state without pretending that PRD / ADR / PLAN already exists.

### GAP-002: Missing Handoff Bootstrap Artifact

Observation（观察）:

- `docs/handoff/HANDOFF-current.md` was absent at session start.
- Handoff is Non-authoritative（非权威）, but the bootstrap sequence still expects it.

Impact（影响）:

- Cross-session recovery loses the human-readable summary layer.

Needed Governance Support（需要的治理支持）:

- A rule for creating an initial Handoff（交接） when no authoritative state exists.

### GAP-003: Project Context Reference Cannot Resolve

Observation（观察）:

- `docs/project/` is absent.
- No runtime state exists to declare the `project_context` reference.

Impact（影响）:

- Project facts, subsystem boundaries, and domain terms cannot be resolved through the expected Harness path.

Needed Governance Support（需要的治理支持）:

- An explicit gate that distinguishes Missing Project Context（缺失项目上下文） from Architecture Drift（架构漂移）.

### GAP-004: MCP-Specific Governance Is Only Generic

Observation（观察）:

- `.ai/rules/api-contract.md` contains useful MCP / Tool contract requirements.
- The Harness does not currently provide an MCP-specific checklist for tool discovery, schema validation, side effects, transport, resource exposure, prompt/tool injection risk, or secret-bearing integration settings.

Impact（影响）:

- Real MCP projects require repeated manual interpretation of generic API and security rules.

Needed Governance Support（需要的治理支持）:

- A dedicated MCP Governance Checklist（MCP 治理清单） covering Tool Contracts（工具契约）, Resource Contracts（资源契约）, Prompt/Tool Boundary（提示词/工具边界）, Side Effects（副作用）, and Secret Handling（密钥处理）.

### GAP-005: Source Project Discovery Is Outside The Harness Contract

Observation（观察）:

- The user referenced `private-source-tool`; its real path had to be supplied out of band.
- `partner-plugin-project` was found by filesystem search rather than through Harness state or Project Context.

Impact（影响）:

- The ADR Current Reality gate depends on ad hoc source binding before it can verify coupling or responsibility overlap.

Needed Governance Support（需要的治理支持）:

- A documented External Source Binding（外部源绑定） mechanism for refactor projects, including source path, comparison target path, and allowed read scope.

### GAP-006: MCP Tool Contract Extraction Is Manual

Observation（观察）:

- MCP tools in `private-source-tool` are registered from Python function signatures and docstrings.
- Tool side effects are spread across `mcp_server.py`, the private lead repository, and the private audit logger.
- The Harness has generic MCP / Tool contract rules but no standard extraction report format.

Impact（影响）:

- Current Reality checks must manually assemble Tool Name（工具名）, Input Schema（输入结构）, Output Shape（输出形态）, Error Behavior（错误行为）, and Side Effects（副作用）.

Needed Governance Support（需要的治理支持）:

- A standard MCP Tool Inventory（MCP 工具清单） artifact or checklist for ADR / PLAN use.

### GAP-007: Cross-Repository Responsibility Drift Has No First-Class Gate

Observation（观察）:

- The target boundary says `partner-plugin-project` should own Skill / Knowledge / Workflow.
- Current `partner-plugin-project` also owns runtime tool registration, OCR / LLM integration, data assumptions, and deterministic calculation logic.

Impact（影响）:

- Harness can classify this as Architecture Drift（架构漂移）, but it has no specific Cross-Repository Responsibility Drift（跨仓职责漂移） gate or report template.

Needed Governance Support（需要的治理支持）:

- A cross-repository boundary review checklist for refactors that split an existing capability across multiple projects.

### GAP-008: Secret Presence Check Needs A Safe Mode

Observation（观察）:

- `private-source-tool` contains a real `.env` file.
- Security rules correctly say not to read secret-bearing `.env*` files unless necessary, but the Harness does not define a standard safe command set for confirming presence, ignore status, tracked status, and variable names without exposing values.

Impact（影响）:

- Agents must improvise secret-safe inspection patterns.

Evidence（证据）, added 2026-08-29 during PLAN-0002-T4:

- The pre-baseline Secret And Private-Data Review（密钥与私有数据审查） was first run with the improvised idiom `grep ... 2>/dev/null || echo clean`.
- The shell had an empty `LANG`, so under the C locale BSD grep rejected a multibyte pattern and exited 2 without printing matches.
- `|| echo clean` treats exit 2 identically to exit 1, so a Validator Execution Failure（验证器执行失败） was reported as a clean result.
- The scan was rerun under a UTF-8 locale with explicit exit-code classification and found private-data matches in 13 files that the first pass had declared clean.
- A security gate that cannot distinguish "no match" from "the check did not run" is not a gate.

Expected Behavior（期望行为）:

- Secret / Private Data Validation（密钥 / 私有数据验证） must use a Deterministic Validator（确定性验证器）, not an improvised shell pipeline.
- The validator must report exactly three outcomes: `PASS`, `MATCH_FOUND`, `TOOL_ERROR`.
- `TOOL_ERROR` is a gate failure. It must never be collapsed into `PASS`.
- The pattern `command || echo clean`, and any equivalent that maps a non-zero validator exit to success, is forbidden.
- The validator must fix its own locale and encoding rather than inheriting the caller's environment.

Needed Governance Support（需要的治理支持）:

- A Secret Inventory Safe Mode（密钥清单安全模式） that records paths, tracking status, variable names from examples/code, and redaction policy without reading real secret values.
- A shipped deterministic validator implementing the three-outcome contract above, so agents do not improvise scan commands per project.

Scope Observation（范围观察）, recorded 2026-08-29 as evidence only:

- This gap is framed around Secrets（密钥）, but PLAN-0002-T4 found zero secrets and still had to stop. The actual release risk was Private Paths（私有路径）, Internal Identifiers（内部标识）, and Private Infrastructure References（私有基础设施引用） in governance documents, plus unresolved Generated Runtime Ownership（生成运行时归属） and License Boundary（授权边界）.
- A future Harness Review should consider promoting this gap into an Open-Source Release Safety Gate（开源发布安全门禁） covering at least: Secrets, Credentials, Private paths, Internal identifiers, Private infrastructure references, Generated runtime ownership, and License boundary.
- This is recorded as evidence only. It does not expand the scope of PLAN-0002, and it was not applied to `ai-codeops-harness`.

### GAP-009: Project Context Contract Reference Is Missing Locally

Observation（观察）:

- `AGENTS.md` says Project Context（项目上下文） follows `docs/harness/PROJECT-CONTEXT-CONTRACT.md`.
- This repository did not contain that contract file when Project Context was initialized for Task 1.

Impact（影响）:

- Agents can create a minimal `docs/project/PROJECT.md`, but cannot validate its shape against the referenced local contract.

Needed Governance Support（需要的治理支持）:

- The Harness install should include the referenced Project Context Contract（项目上下文契约） or define a fallback location.

### GAP-010: Continuation Request Can Mix Task ID And Later Task Semantics

Observation（观察）:

- During PLAN-0001-T4, the continuation request named `PLAN-0001-T4` but included completion reporting fields for MCP Server / Tool runtime behavior, which belongs to PLAN-0001-T5 in the approved PLAN.

Impact（影响）:

- The agent had to infer that the approved PLAN task ID remains authoritative and avoid executing the later MCP adapter task early.

Needed Governance Support（需要的治理支持）:

- A standard Task Request Consistency Check（任务请求一致性检查） that compares the named task, approved task goal, user-added constraints, and requested completion report before implementation.

### GAP-011: MCP SDK Schema Fidelity Needs An Explicit Gate

Observation（观察）:

- FastMCP-style function registration was available in the installed SDK, but the generated tool schema did not preserve the accepted contract's cross-field and strict-object constraints such as `anyOf` and `additionalProperties: false`.
- The implementation used the low-level MCP `Server` API to declare the accepted input and output schemas explicitly.

Impact（影响）:

- A real MCP project can appear to expose a valid tool while silently weakening the accepted Tool Contract（工具契约） at discovery time.

Needed Governance Support（需要的治理支持）:

- A T5-level MCP Schema Fidelity Check（MCP 结构保真检查） that compares the discovered runtime schema against the accepted contract and documents when low-level registration is required.

### GAP-012: Documentation Language Policy Should Be Explicit

Observation（观察）:

- Current project governance artifacts mix English headings and English narrative with required Chinese explanations for selected terms.
- The Harness does not provide a project-level Documentation Language Policy（文档语言策略） or a configurable default for governance artifact language.

Impact（影响）:

- Cross-AI and human review can become inconsistent about whether PRD / ADR / PLAN / Handoff / State summaries should be primarily English, Chinese, or bilingual.
- Agents may spend task scope on broad translation instead of the requested governance or implementation work.

Needed Governance Support（需要的治理支持）:

- Harness default governance documents should be Simplified Chinese（简体中文）.
- Technical terms should keep English with Chinese explanation, for example Tool Contract（工具契约） and Runtime State（运行状态）.
- Code, API, Schema, CLI, file paths, package names, and identifiers should remain English.
- Future Harness versions should consider a configurable `documentation_language` setting.
- Current project work should record this gap only and must not modify the Harness Source（Harness 源码）.

### GAP-013: Approval Record Is Not Machine-Readable

Observation（观察）:

- Human Approval（人工审核） of a PLAN is expressed only as prose in the PLAN document `Status:` line, plus a status enum in `.ai/state/execution-state.yaml`.
- There is no structured Approval Record（审批记录） carrying approver, approval date, approved scope, and the decisions confirmed at approval time.
- During Cross-Agent Recovery（跨智能体恢复） after a Token Limit Interruption（Token 限额中断）, the recovering agent had to infer approval status by cross-reading three separate documents and comparing their wording.

Impact（影响）:

- A recovering agent can only infer approval, which is exactly the kind of inference the Harness forbids for task status.
- Approval-time decisions, such as a chosen license holder or an approved CI version matrix, are not recorded anywhere the next agent can read, so they must be re-asked or re-guessed.
- Divergent wording across PLAN, State, and Handoff has no authoritative tie-breaker for approval, unlike task status, which Current Reality（当前事实） can settle.

Needed Governance Support（需要的治理支持）:

- A first-class Approval Record（审批记录） schema in Runtime State（运行状态） with approver identity, approval timestamp, approved scope, approved task range, and confirmed decisions.
- An explicit rule that Approval Status（审批状态） is authoritative in State only, with the PLAN document as the human-readable mirror.
- A Cross-Agent Recovery（跨智能体恢复） step that reads the Approval Record before selecting a READY Task.

### GAP-014: Validation Evidence Has No Environment Provenance

Observation（观察）:

- Checkpoint（检查点） validation entries record commands such as `python3 -m unittest discover -s tests` without recording which interpreter, version, or dependency environment actually ran them.
- In this workspace the MCP SDK resolves under only one of several installed interpreters. Re-running the recorded command with the shell default interpreter produced `FAILED (errors=2)` from a missing SDK import.
- The recovering agent had to reverse-engineer the correct interpreter from `__pycache__` bytecode tags and site-packages layout before it could tell an environment difference from a code regression.

Impact（影响）:

- A recorded PASS is not reproducible by the next agent, because the environment that produced it is not part of the evidence.
- An environment mismatch is easily misclassified as State Drift（状态漂移） or a Validation Failure（验证失败）, which can trigger an unnecessary stop or, worse, an unnecessary rollback.
- Cross AI（跨 AI） and cross machine recovery cannot distinguish NOT RUN（未执行） from BLOCKED（阻塞） without this provenance.

Needed Governance Support（需要的治理支持）:

- A required `validation_environment`（验证环境） block in Checkpoint（检查点） recording interpreter path, language version, and dependency resolution notes for executed validation.
- A rule that Executed Test（已执行测试） evidence is valid only when its environment is recorded.
- A Reproduce Validation（复现验证） step in Cross-Agent Recovery（跨智能体恢复） that resolves the recorded environment before classifying a failing rerun as Drift（漂移）.

## Non-Actions

The Harness Source（Harness 源码） was not modified.

Harness gaps were recorded only in this file and were not applied to `ai-codeops-harness`.

GAP-013 and GAP-014 were recorded during Cross-Agent Recovery（跨智能体恢复） on 2026-08-29 as observation-only findings.

GAP-008 was extended on 2026-08-29 with evidence from PLAN-0002-T4, a strengthened Expected Behavior（期望行为）, and an Open-Source Release Safety Gate（开源发布安全门禁） scope observation. No new gap number was created for that finding.

None of these were applied to `ai-codeops-harness`. Managed-file integrity was verified: all 19 installer-managed files match their recorded sha256.
