# PLAN-0002: V0.1 Release Preparation

Status: Approved

Date: 2026-08-29

Approved: 2026-08-29

Approval Basis（批准依据）:

- Human Approval（人工审核） granted by the project owner in the Cross-Agent Recovery（跨智能体恢复） session on 2026-08-29.
- Approved Scope（批准范围）: Task 1 through Task 5 as written, executed consecutively.
- Confirmed Decision 1（已确认决策 1）: MIT `LICENSE` uses Neutral Personal Copyright Text（中性个人版权文本）; the private platform vendor entity must not be introduced.
- Confirmed Decision 2（已确认决策 2）: Minimal GitHub CI validates Python 3.11 only; the version matrix must not be expanded.
- Confirmed Decision 3（已确认决策 3）: Two Cross-Agent Recovery findings are appended to `docs/harness/HARNESS-GAPS.md` as observation-only.
- Confirmed Decision 4（已确认决策 4）: `ai-codeops-harness` Source（Harness 源码） must not be modified.
- Approved Stop Conditions（批准的停止条件）: Secret / Private Data Review anomaly, Drift（漂移）, Validation Failure（验证失败）, Security Boundary Change（安全边界变更）, Release Approval（发布审批）.

Related:

- Completed PLAN: `docs/plan/PLAN-0001-mcp-ess-open-source-migration.md`
- Accepted ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`
- Accepted MCP Tool Contract: `docs/contracts/mcp-tools.md`

## Goal

Prepare `mcp-ess-proposal` V0.1 Release Candidate（发布候选） for first tracked baseline and later open-source release without changing Core v0 architecture, MCP Tool Contract（MCP 工具契约）, or runtime behavior.

## Router Output

Workflow: PLAN

Reason:

- Business goal is clear: Release Preparation（发布准备） only.
- Architecture is clear and unchanged by ADR-0001.
- The requested work spans multiple files and governance artifacts: `LICENSE`, GitHub CI, README, secret/private-data review, Handoff（交接）, Runtime State（运行状态）, and Checkpoint（检查点）.
- GitHub CI changes affect Development Workflow（开发工作流） and require a validation plan.
- Direct IMPL would skip the required approval gate for the new release-preparation task sequence.

Known:

- PLAN-0001 has passed Human Final Review（人工最终审核）.
- Current version is V0.1 Release Candidate.
- Core v0 exposes only `generate_ess_proposal`.
- Core v0 remains deterministic, side-effect free, zero-secret, and stdio-only.
- No MCP feature, Provider（供应商）, OCR, LLM, CRM, DB, Lead（线索）, authentication, Remote HTTP（远程 HTTP）, or GitHub publication will be added in this phase.
- Harness gaps remain observation-only in `docs/harness/HARNESS-GAPS.md`.

Unknown:

- The final public GitHub repository URL is not known, so README badges or repository-specific links must not be invented.
- Whether CI should validate additional Python versions beyond the minimum supported Python 3.11 is a release-maintainer choice; the minimal approved default is Python 3.11 only unless Human Approval expands it.

Required Context:

- `AGENTS.md`
- `.ai/workflows/router.md`
- `.ai/workflows/plan.md`
- `.ai/rules/security.md`
- `.ai/rules/testing.md`
- Completed PLAN-0001
- ADR-0001
- MCP Tool Contract
- Current README, pyproject, tests, package layout, and Harness state

## Preconditions

- PLAN-0001 is Complete（已完成） by Human Final Review.
- Release Preparation must not modify the accepted MCP Tool Contract.
- Release Preparation must not introduce new MCP tools or runtime capabilities.
- Old `private-source-tool` must not be modified.
- GitHub publication is explicitly out of scope.

## Current Reality

- `pyproject.toml` declares MIT license metadata.
- No `LICENSE` file exists.
- No `.github/workflows` directory or CI workflow exists.
- README explains project purpose, scope, non-goals, configuration, runtime path, and validation commands.
- The repository has no commits and all project files are currently untracked.
- Core runtime has no required environment variables and no `.env` loading.
- T8 validation built a wheel, installed it into `/private/tmp/mcp-ess-proposal-install`, verified bundled fixtures, and validated source and installed-package stdio runtime.

## Change Set

Expected changes:

- Add MIT `LICENSE`.
- Add minimal GitHub Actions CI workflow.
- Update README only for open-source completeness, such as license, release candidate status, CI validation, and support boundaries.
- Run final secret/private-data review before first tracked baseline.
- Update Handoff, Runtime State, and Checkpoint for Release Preparation tasks.

Forbidden changes:

- No MCP Tool Contract changes.
- No new MCP tool registration.
- No Provider / OCR / LLM / DB / CRM / Lead / authentication / Remote HTTP capability.
- No changes to old `private-source-tool`.
- No GitHub publication.
- No Harness Source（Harness 源码） changes.

## Ordered Tasks

### Task 1: Add MIT License

Goal:
Align repository files with `pyproject.toml` MIT metadata.

Target:
`LICENSE`, optionally README license section.

Dependencies:
None.

Changes:

- Add standard MIT License text.
- Use neutral copyright holder text if no legal owner is provided.
- Do not change package code or MCP behavior.

Validation:

- Confirm `LICENSE` exists.
- Confirm README and `pyproject.toml` license references are consistent.
- Confirm no runtime/source changes.

### Task 2: Add Minimal GitHub CI

Goal:
Add CI that runs the existing validation without expanding functionality.

Target:
`.github/workflows/ci.yml`.

Dependencies:
Task 1.

Changes:

- Use GitHub Actions with Python 3.11.
- Install the package with dev/test requirements sufficient for existing tests.
- Run:
  - `python -m compileall src tests`
  - `python -m unittest discover -s tests`
  - package build validation equivalent to the local wheel check.
- Do not add release, deploy, publish, secret, provider, or remote integration jobs.

Validation:

- Parse/review workflow YAML.
- Confirm CI commands match existing local validation.
- Confirm no secret names or deployment permissions are introduced.

### Task 3: README Open-Source Completeness Review

Goal:
Make README sufficient for a third-party reviewer of the V0.1 Release Candidate.

Target:
`README.md`.

Dependencies:
Tasks 1 and 2.

Changes:

- Add license reference.
- Add CI / validation section if needed.
- Clarify Release Candidate status and non-goals.
- Do not add unapproved roadmaps or feature promises.

Validation:

- Documentation review against ADR-0001 and the accepted MCP Tool Contract.
- Check README does not introduce provider, OCR / LLM, CRM, DB, Lead, authentication, Remote HTTP, or private brand scope.

### Task 4: First Tracked Baseline Secret And Private-Data Review

Goal:
Verify the project is safe to stage for a first tracked baseline.

Target:
Whole repository, excluding generated caches and ignored runtime files.

Dependencies:
Tasks 1 through 3.

Changes:

- No feature changes.
- Run final secret/private-data review before any `git add`.
- Record results in Harness state and Handoff.

Validation:

- `git status --short --untracked-files=all`
- `git ls-files .env .env.example`
- `git check-ignore -v .env .env.local .env.example`
- Secret-safe grep for provider keys, database URLs, private brand strings, CRM/Lead write paths, OCR/LLM/provider coupling, upload/runtime JSONL paths.
- Confirm old `private-source-tool` was not modified by this phase.

### Task 5: Release Preparation Closeout

Goal:
Confirm Release Preparation is complete and ready for first tracked baseline / human release decision.

Target:
Handoff, Runtime State, Checkpoint, README, Project Context if affected.

Dependencies:
Tasks 1 through 4.

Changes:

- Update Harness recovery artifacts.
- Record validation and any remaining release risks.
- Do not publish to GitHub.

Validation:

- `python -m compileall src tests`
- `python -m unittest discover -s tests`
- package build check.
- installed-package stdio smoke if dependencies are available locally.
- state/checkpoint YAML parse.
- final documentation and scope review.

## Validation Plan

Required before Release Preparation can be marked Complete（完成）:

- Existing unit and MCP runtime tests must pass.
- Package build/install validation should pass or be explicitly reported if blocked by environment.
- GitHub CI workflow must be reviewed for minimal scope and no secret/deploy permissions.
- Secret/private-data review must pass before first tracked baseline.
- README must align with ADR-0001, PLAN-0001, and MCP Tool Contract.

## Risks

- Adding CI can accidentally introduce publishing or secret permissions; keep the workflow test-only.
- README can accidentally over-promise future provider/OCR/HTTP/auth behavior; keep it scoped to Core v0.
- MIT license holder may require human legal confirmation if a specific owner is desired.
- Repository has no tracked baseline; final diff review must use status/file inventory until the first commit exists.

## Documentation Impact

- README license / validation details.
- Project Context if release status changes.
- Handoff and Runtime State after each approved implementation task.
- Harness gaps remain observation-only.

## Ready To Enter IMPL

Yes.

Reason（原因）: Human Approval（人工审核） was granted on 2026-08-29 with the confirmed decisions recorded in Approval Basis（批准依据）. The two PLAN Unknown（未知项） entries are now resolved: the MIT copyright holder is Neutral Personal Copyright Text（中性个人版权文本）, and CI remains Python 3.11 only. The final public GitHub repository URL remains unknown, so repository-specific badges and links must still not be invented.
