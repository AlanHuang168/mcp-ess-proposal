# ADR-0002: Open-Source Governance Artifact Boundary

Status: Accepted

Accepted: 2026-08-29

Status Rationale（状态理由）: this ADR was held at `Proposed` while D4 was unresolved, because the Harness ADR lifecycle defines no Partially Accepted（部分接受） status and marking it `Accepted` would have asserted a decision that had not been made. All four decisions now have a Human Decision, so the document moves to `Accepted` under the standard vocabulary.

Date: 2026-08-29

Amends: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`

Supersedes: none. ADR-0001 remains Accepted（已接受） and its Core boundary decision is unchanged.

Related:

- Approved PLAN: `docs/plan/PLAN-0002-release-preparation.md`
- Escalated Task: `PLAN-0002-T4` First Tracked Baseline Secret And Private-Data Review
- Accepted MCP Tool Contract: `docs/contracts/mcp-tools.md`
- Harness Gaps: `docs/harness/HARNESS-GAPS.md`

## Context

ADR-0001 decided which capabilities may enter the open-source Core（核心）: MCP Server / Tool / Data / Integration stay, while private brand, Lead（线索）, CRM, private database writes, provider calls, OCR / LLM, and prompt logic stay out.

ADR-0001 scoped that decision to **Source Code（源代码）**. It never decided anything about the **Governance Artifact（治理产物）** layer that the governed migration itself produced: ADR, PLAN, Contract, Project Context, System Map, Handoff（交接）, Harness Gaps, Runtime State（运行状态）, and Checkpoint（检查点）.

PLAN-0002-T4 executed the pre-baseline Secret And Private-Data Review（密钥与私有数据审查） and found that the Source Code boundary holds, but the Governance Artifact layer would publish private internal detail at the first tracked baseline. That is an Architecture Drift（架构漂移） against the intent of ADR-0001, not an implementation bug, so IMPL escalated instead of editing the Accepted ADR.

## Current Reality

Verified on 2026-08-29 by a deterministic validator over all 61 files in the first-baseline scope. The repository has no commits, so nothing has been published yet.

### Source Code boundary holds

- No secret value exists anywhere in scope: no API key, token, credential, private key block, connection string, or high-entropy literal.
- Runtime source, fixtures, packaging metadata, `LICENSE`, CI workflow, and README are free of private coupling.
- The one private-name match in test code is a deliberately split string literal in a negative test asserting that old private settings are absent. It is correct and is not an exposure.

### Governance Artifact layer does not hold

Private internal detail is present in 13 governance and state files, by category:

| Category | Occurrences | Nature |
| --- | --- | --- |
| Private local absolute path | 17 | Discloses the developer account name and the private platform directory layout of a machine, not of the product. |
| Private brand / private project identifier | 148 (excluding the benign test literal) | Names the private organization, platform, and source tool. |
| Private configuration variable name | 13 | Names provider credential and internal database configuration of the private system. |
| Internal database table name | 2 | Names a private lead-persistence table. |
| Private runtime storage path | 4 | Names private lead and audit storage files. |

Concentration: the Accepted ADR-0001 holds 71 occurrences and PLAN-0001 holds 40, because both record migration evidence about the private source. The remaining 11 files hold the rest.

Not all of this is equal. The private brand and the responsibility descriptions carry real architectural value: they explain **why** Core excludes Lead, CRM, database writes, and OCR / LLM. The local absolute paths, the table name, the storage file names, and the credential variable names carry no open-source architectural value at all.

### `.ai/` is not one thing

`.ai/VERSION` declares `ai-codeops-harness` 0.1.0 with a manifest of 19 installer-managed files and their sha256. Verified against the working tree:

- **18 files under `.ai/` are installer-managed third-party content**: `.ai/workflows/*`, `.ai/roles/*`, `.ai/rules/*`. All 19 managed files match their recorded sha256, confirming the Harness Source（Harness 源码） was not modified.
- **13 files under `.ai/state/**` are project-owned Runtime Facts（运行时事实）**: `execution-state.yaml` and the per-task Checkpoints. These are produced by this project, not by the installer.
- `.ai/VERSION` is the installer manifest and is not self-listed.
- **`AGENTS.md` at the repository root is also installer-managed.** It is listed in the manifest and matches its recorded sha256.

So the ownership question is not "is `.ai/` in or out". `.ai/` is a mixed directory, and one installer-managed file already sits at the repository root outside `.ai/` entirely.

## Decision Problem

ADR-0001 defined a boundary for Source Code only. The first tracked baseline and any later open-source release will publish Governance Artifacts and installer-managed Harness Runtime as well.

Two questions need an architecture decision:

1. **What is the publication boundary for Governance Artifacts, and what must be sanitized before they cross it?**
2. **Who owns installer-managed Harness Runtime in this repository, and does this project's `LICENSE` legitimately cover it?**

## Options

### Question 1: Governance Artifact publication

**Option 1A — Publish as written.** Zero effort, full traceability. Publishes developer machine layout, private organization internals, an internal table name, and private credential variable names that no open-source consumer needs. Rejected: it publishes private detail that was never an accepted decision, and git history makes it permanent.

**Option 1B — Exclude `docs/` and `.ai/` from the public repository.** Safe and cheap. Destroys the governance value of the release: an open-source consumer could not see why Core excludes Lead, CRM, and OCR / LLM, which is the most useful part of the ADR-0001 record. Rejected by the project owner.

**Option 1C — Publish Governance Artifacts after Open-Source Sanitization（开源脱敏）.** Keeps architectural reasoning, removes internal identifiers with no open-source value. Costs a sanitization pass over 13 files and requires editing an Accepted ADR, so it needs approval. **Proposed.**

**Option 1D — Maintain a separate public governance mirror.** Keeps the private record intact and publishes a clean one. Rejected for current scale: two divergent copies of the same ADR is a drift source, and this project has one repository and one maintainer.

### Question 2: Harness Runtime ownership

**Option 2A — Track `.ai/` and `AGENTS.md`, publish under this repository's MIT `LICENSE`.** Simple and reproducible for consumers. Asserts MIT over third-party content whose own license was never established here. Rejected as a default: a project `LICENSE` file cannot grant rights over content the project does not own.

**Option 2B — Do not track installer-managed files; consumers re-run the installer.** Clean ownership. Requires the `.ai/state/**` Runtime Facts to be separated out and still tracked, since Cross-Agent Recovery（跨智能体恢复） depends on them. Costs a `.gitignore` split and a documented install step.

**Option 2C — Track everything but record third-party ownership explicitly** through a NOTICE / third-party license section that carves the Harness out of the MIT grant. Preserves reproducibility without misrepresenting ownership. Requires knowing the Harness's actual license, which this repository does not currently record.

**Option 2D — Defer, and keep the first baseline free of installer-managed files.** Unblocks the baseline without deciding ownership prematurely.

Question 2 needs the Harness's actual license terms before a decision can be justified, and this repository does not contain them. **No option is proposed for Question 2 in this ADR.**

## Decision Record（决策记录）

Human Decision（人工决策） of 2026-08-29:

| Decision | Outcome | Note |
| --- | --- | --- |
| D1 Governance Artifact Boundary | **Accepted（已接受）** | Source Code and Governance Artifact are both in Open-Source Release Review scope. |
| D2 Open-Source Sanitization | **Accepted（已接受）** | Governance and state artifacts must be sanitized before the first public baseline. Architecture Reasoning, Decision, and Evidence are retained. Private paths, internal project identifiers, database table names, runtime paths, and private configuration variable names are removed or abstracted. |
| D3 Release Safety Gate | **Accepted（已接受）** | Deterministic Validator required. Status must distinguish at least PASS, MATCH_FOUND, TOOL_ERROR. TOOL_ERROR must fail closed. Collapsing validator execution failure into clean or pass is forbidden. |
| D4 Harness Runtime Ownership / Licensing | **Accepted（已接受）** | Consumer-side minimal redistribution policy, decided 2026-08-29 after inspecting the Harness Source Repository. |

All four decisions are binding governance from the date above.

### D4 Accepted Decision（已接受决策）: Consumer-Side Minimal Redistribution Policy

The first public baseline of `mcp-ess-proposal` V0.1 / V0.2 does **not** Git track or redistribute `ai-codeops-harness` installer-managed artifacts. Excluded, as confirmed by the Harness manifest and `.ai/VERSION`:

- `AGENTS.md`
- `.ai/rules/**`
- `.ai/roles/**`
- `.ai/workflows/**`
- `.ai/VERSION`
- any other Harness-managed artifact

`.ai/state/**` is treated separately. It is confirmed project-generated Runtime Facts（运行时事实）, so it **may** enter the public baseline, but only after passing Open-Source Sanitization（开源脱敏） and the Release Safety Gate（发布安全门禁）.

Scope of this decision（本决策的适用范围）: this is the `mcp-ess-proposal` Consumer Distribution Policy（消费方分发政策） only. It must **not** be read back as a global distribution policy for `ai-codeops-harness`.

Future consumers who need the Harness Runtime should generate it through the `ai-codeops-harness` installer, rather than relying on this repository to distribute installer-managed runtime.

Rationale（理由）: the Harness ownership model answers who owns which file for update purposes, but states no consumer-side distribution, attribution, or tracking policy. Rather than infer one, this project declines to redistribute. That is the minimal choice that is correct under any upstream policy the Harness may later adopt.

### D4 Evidence Gathered（已收集证据）

Read-only inspection of the Harness Source Repository on 2026-08-29. This is evidence only; no D4 determination is made here.

| Required evidence | Status | Finding |
| --- | --- | --- |
| LICENSE | **Found** | The Harness is MIT licensed under an individual copyright holder. MIT permits redistribution and requires the copyright notice be preserved. |
| manifest/harness.yaml | **Found** | Declares runtime mappings with explicit `owner`, `update_policy: managed`, and `conflict_policy: abort_on_user_change`. Rules, roles, and workflows are `owner: harness`. The root adapter file is `owner: adapter`. |
| Installer Contract | **Found** | Defines four ownership categories: Harness-owned, Adapter-owned, User-owned, and Generated runtime. Ownership is resolved by recorded path and SHA-256, not by timestamps or naming. |
| Ownership Model | **Found** | Confirms `.ai/` is mixed by design. `.ai/state/` holds project Runtime Facts, while rules, roles, and workflows are Harness-owned. `.ai/VERSION` is classified as Generated runtime. |
| Generated Runtime policy | **Partial** | The Runtime Model defines what Generated Runtime is and where it lives, but states no policy on whether a consumer project should Git track it. |
| Adapter distribution policy | **Not found** | No distribution, redistribution, attribution, or consumer-licensing policy exists anywhere in the Harness documentation. A search for license, copyright, redistribution, and attribution across the Harness docs, README, and contributing guide returned no policy statement. |

Consequence（结果）: the Harness ownership model answers *who owns which file for update purposes*, but it does not answer *how a consumer project should license, attribute, or track those files when publishing*. That second question is unanswered by the authoritative source. D4 resolves it by declining to redistribute, which requires no assumption about upstream intent.

## Proposed Decision

### D1: Governance Artifact Boundary（治理产物边界）

Extend the ADR-0001 boundary to cover Governance Artifacts. Source Code（源代码） and Governance Artifact（治理产物） are both in Release Review（发布审查） scope. A release is safe only when both pass.

### D2: Open-Source Sanitization（开源脱敏）

Governance Artifacts may be published after sanitization. Apply by category:

| Category | Treatment |
| --- | --- |
| Private local absolute path | Replace with `<PRIVATE_SOURCE_ROOT>` or `<LOCAL_WORKSPACE>` |
| Internal database table name | Replace with a responsibility description, for example internal database table |
| Private runtime storage path | Replace with a responsibility description, for example private runtime storage, private lead persistence |
| Private configuration variable name | Replace with a semantic description, for example provider credential, internal database configuration |
| Other internal implementation identifiers with no open-source architectural value | Remove |

Retain architectural reasoning, decision rationale, boundary justification, and responsibility descriptions. Sanitization removes identifiers, never removes the decision record.

### D3: Release Safety Gate（发布安全门禁）

Secret And Private-Data Review is promoted from a PLAN task step to a standing release gate covering Secrets, Credentials, Private paths, Internal identifiers, and Private infrastructure references, over both Source Code and Governance Artifacts.

The gate must use a Deterministic Validator（确定性验证器） reporting exactly `PASS`, `MATCH_FOUND`, or `TOOL_ERROR`. `TOOL_ERROR` is a gate failure, never a pass. Shell idioms that collapse validator failure into success are forbidden; this is recorded as evidence in `docs/harness/HARNESS-GAPS.md` GAP-008.

### D4: Harness Runtime ownership

Outcome: Accepted as the Consumer-Side Minimal Redistribution Policy. See Decision Record above. The option analysis below is retained as the historical basis; the accepted outcome corresponds to Option 2B combined with Option 2D.

No ownership decision was proposed at the time of writing. Until a decision is Accepted, one constraint applies:

**The project `LICENSE` must not be treated as covering installer-managed Harness Runtime.** MIT metadata on this project does not extend to `ai-codeops-harness` content by default. This constraint applies to `.ai/workflows/*`, `.ai/roles/*`, `.ai/rules/*`, `.ai/VERSION`, and to `AGENTS.md` at the repository root.

The deferred decision must resolve: whether installer-managed files are Generated Runtime（生成的运行时） or Project Source（项目源码）; whether they should be Git tracked; how `LICENSE` and ownership are handled; and whether open-source consumers should regenerate them through the installer. It must also address that `.ai/` is a mixed directory whose `.ai/state/**` Runtime Facts are project-owned and are required for Cross-Agent Recovery.

## Consequences

Positive:

- The publication boundary becomes explicit instead of assumed, for both layers.
- The governance record stays public and useful, which was the project owner's stated goal.
- Release safety becomes a repeatable gate with a defined failure mode rather than an ad hoc grep.
- The license boundary stops being decided by default.

Negative:

- A sanitization pass is required over 13 files before the first baseline.
- Editing an Accepted ADR requires this amendment, adding one approval cycle.
- Sanitized governance documents lose some evidence precision relative to the private original.
- The Harness ownership question stays open and continues to block a complete release decision.

Risks:

- Over-sanitization could remove the reasoning that makes the ADR record worth publishing. Mitigated by D2 retaining responsibility descriptions.
- Under-sanitization leaves an identifier in git history permanently. Mitigated by D3 requiring the validator to pass before the first `git add`.
- Sanitizing ADR-0001 edits an Accepted decision record. The original wording is preserved in this amendment's Current Reality only as categories and counts, never as reproduced identifiers.
- If the Harness license turns out to forbid redistribution, a baseline that already tracked those files would need history rewriting. Mitigated by deciding before the first commit.

## Documentation Impact

On acceptance:

- ADR-0001 gains a reference to this amendment and is sanitized per D2.
- PLAN-0001, PLAN-0002, Contract, Project Context, System Map, Handoff, Harness Gaps, Runtime State, and the affected Checkpoints are sanitized per D2.
- README gains no change from this ADR; support boundaries are unaffected.
- A new PLAN is required to execute sanitization and to re-run the release gate. PLAN-0002 scope is not expanded.

## Ready To Enter PLAN

Yes.

Reason（原因）: all four decisions are Accepted and the public baseline inventory is now determined. Execution proceeds under `docs/plan/PLAN-0003-contract-v0-2-implementation.md`, which carries the sanitization, release safety gate, and baseline cleanup tasks that PLAN-0002 left blocked.
