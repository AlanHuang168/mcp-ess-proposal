# PLAN-0003: Contract v0.2 Implementation And Release Closeout

Status: Approved

Date: 2026-08-29

Approved: 2026-08-29

Approval Basis（批准依据）:

- Human Decision（人工决策） of 2026-08-29 approved AMENDMENT-0001 C1 through C4 and authorized continuous PLAN to IMPL to Validation execution without a second approval gate after PLAN creation.
- Authorized end state（授权终点）: Release Candidate Ready（发布候选就绪）.
- Not authorized（未授权）: `git push`, GitHub Release, package registry publish, public announcement.

Related:

- Accepted Contract Amendment: `docs/contracts/AMENDMENT-0001-generate-ess-proposal-consumption-and-tariff.md`
- Accepted Contract: `docs/contracts/mcp-tools.md`
- Accepted ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`
- Accepted ADR: `docs/adr/ADR-0002-open-source-governance-artifact-boundary.md`
- Blocked PLAN resumed by this plan: `docs/plan/PLAN-0002-release-preparation.md`

## Goal

Implement MCP Tool Contract Core v0.2 for `generate_ess_proposal`, then complete the Release Closeout（发布收口） that PLAN-0002 left blocked, up to Release Candidate Ready.

## Stop Conditions（停止条件）

Stop only on: Architecture Drift（架构漂移）, Scope Expansion（范围扩张）, Security Issue（安全问题）, Destructive Action（破坏性操作）, a Validation Failure（验证失败） not fixable within scope, or a new genuine Human Decision.

## Ordered Tasks

### Task 1: Contract v0.2 Document Update

Target: `docs/contracts/mcp-tools.md`.

Changes: add `tariff_myr_per_kwh` input; add `tariff_source`, `consumption_source`, and `financial.investment_scope` outputs; add `INCONSISTENT_CONSUMPTION_INPUT`; document tariff resolution, consumption precedence, the ±10% tolerance, and the v0.1 to v0.2 compatibility note.

Validation: document review against AMENDMENT-0001; confirm no field removed or renamed.

### Task 2: Core Implementation

Target: `src/mcp_ess_proposal/models.py`, `calculator.py`.

Changes: accept and validate `tariff_myr_per_kwh`; implement the approved resolution order and precedence rule; implement ±10% consistency validation returning `INCONSISTENT_CONSUMPTION_INPUT`; emit `tariff_source`, `consumption_source`, and `investment_scope`; fix the non-residential bill conversion to use the customer type's own tariff.

Validation: unit tests; deterministic reproduction of E1 through E5.

### Task 3: Server Schema Fidelity

Target: `src/mcp_ess_proposal/server.py`.

Changes: mirror the v0.2 input and output schemas in the low-level tool registration.

Validation: runtime discovery schema compared field by field against the contract document, per GAP-011.

### Task 4: Tests

Target: `tests/`.

Changes: E1 through E5 regression tests; ±10% boundary tests including just inside, exactly at, and just outside; tariff source coverage for all three values; consumption source coverage; `investment_scope` presence when storage is recommended.

Validation: full unit suite.

### Task 5: Runtime And Host Validation

Changes: none.

Validation: stdio MCP `ClientSession` round trip covering initialize, list_tools, and call_tool for success and for the new error path.

### Task 6: Documentation Sync

Target: `README.md`, `docs/data/fixtures.md`.

Changes: document the optional tariff input, the tariff source, and the PV-only investment scope.

Validation: documentation review; scope-drift scan.

### Task 7: Release Safety Gate Implementation

Target: `tools/release_safety_gate.py`.

Changes: implement the ADR-0002 D3 Deterministic Validator（确定性验证器） reporting `PASS`, `MATCH_FOUND`, or `TOOL_ERROR`, failing closed on `TOOL_ERROR`, with a fixed UTF-8 locale.

Validation: run the gate; verify it detects a seeded match and reports `TOOL_ERROR` correctly on an unreadable target.

### Task 8: Open-Source Sanitization

Target: governance documents and `.ai/state/**` entering the public baseline.

Changes: apply the ADR-0002 D2 category mapping. Retain architecture reasoning, decisions, and evidence.

Validation: release safety gate returns `PASS` over the public baseline scope.

### Task 9: Baseline Cleanup

Target: `.gitignore`.

Changes: exclude installer-managed artifacts per ADR-0002 D4 while keeping `.ai/state/**` tracked.

Validation: `git check-ignore` and `git status` confirm the intended public baseline contents.

### Task 10: CI And Baseline Preparation

Validation: full suite; package build; CI workflow review; release safety gate; first tracked baseline commit. No push, release, or publish.

## Forbidden

No new MCP tool. No Provider, OCR, LLM, database, CRM, or Lead capability. No regional tariff dataset expansion. No storage pricing. No modification of the legacy private project or of Harness Source. No push, release, or publish.
