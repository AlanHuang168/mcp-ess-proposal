# CONTRACT AMENDMENT-0001: `generate_ess_proposal` Consumption And Tariff Resolution

Status: Accepted for Core v0.2

Date: 2026-08-29

Accepted: 2026-08-29

Status Vocabulary Note（状态词表说明）: `.ai/rules/api-contract.md` defines no lifecycle vocabulary for contract documents. This amendment follows the Accepted contract's own header convention, `Status: Accepted for Core v0`.

Human Decision（人工决策）, 2026-08-29:

- C1, C2, C3, C4 all Accepted（全部接受）. Contract version is Core v0.2.
- Boundary ruling（边界裁定）: a client may supply a tariff scalar for a single calculation. This is **not** a transfer of ADR-0001 Data Ownership（数据归属）. Ownership of the Tariff Dataset（电价数据集） and Default Tariff（默认电价） remains with Server / Fixtures. The change therefore stays on the PLAN route and does not re-route to ADR.
- Consistency tolerance（一致性容差）: **±10%**. Boundary values must be tested.
- Out-of-tolerance behaviour（超差行为）: **error**, code `INCONSISTENT_CONSUMPTION_INPUT`. Silently選ecting one input is forbidden. Downgrading to a warning is forbidden.
- Financial scope（财务范围）: `investment_scope = "pv_only"`. Storage pricing, total system investment, and battery ROI are explicitly not implemented in this version.
- Scope guard（范围护栏）: no new MCP tool, no Provider, no OCR, no LLM, no database, no regional tariff dataset expansion, no modification of the legacy private project.

Amends: `docs/contracts/mcp-tools.md` (Accepted MCP Tool Contract, Core v0)

Governing ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md` (Accepted, unchanged by this amendment)

Proposed Contract Version（契约版本）: Core v0.2. The Accepted contract is not modified by this document.

## Router Output

Workflow: **PLAN**

Reason（原因）:

- Business goal is clear: the tool must accept a user-supplied tariff, must not silently discard a user-supplied consumption value, and must not let a Host read a PV-only investment figure as a whole-system cost.
- Architecture is unchanged. Every ADR-0001 boundary holds: one public tool, deterministic, side-effect free, zero-secret, stdio-only, no Provider / OCR / LLM / CRM / database / Lead capability.
- The Accepted contract already states that future optional fields may be added compatibly, and reserves ADR / PLAN review for removing or renaming fields.
- The work spans contract, schema, Core calculation, tests, and documentation, and it contains a semantic change with compatibility impact. `.ai/rules/api-contract.md` requires breaking changes to have explicit scope and migration planning, which is PLAN work.

ADR triggers evaluated and **not** met: no subsystem added, removed, or merged; no Data Owner change; no database or schema ownership change; no Provider / Adapter / Webhook change; no sync / async model change; no authentication or authorization change; no significant infrastructure introduced.

One ADR-adjacent question is raised explicitly rather than resolved downstream（一个需人工裁定的边界问题）:

- ADR-0001 Task 4 learning recorded that clients should not supply tariff data in Core v0, and that fixtures are server-owned implementation resources.
- This amendment proposes accepting a single scalar tariff **parameter**, not a tariff file, path, dataset, or configuration source. Server-owned fixtures remain the sole default data source, and the client cannot replace, extend, or address them.
- Assessment: this is a calculation parameter, not a transfer of Data Ownership（数据归属）, so it is not Architecture Drift.
- If the reviewer judges that any client-supplied tariff value crosses the ADR-0001 data boundary, this amendment must be re-routed to ADR before PLAN.

## Contract Drift Evidence

Source（来源）: Claude Code MCP Host End-to-End test, 2026-08-29. Reproduced deterministically against the current implementation before writing this amendment. Evidence Kind（证据类型）: Executed Test（已执行测试）.

### E1: User-supplied tariff is rejected

Input `{"customer_type":"residential","location":"…","monthly_kwh":600,"tariff_myr_per_kwh":0.60}` returns:

```json
{"status":"error","code":"VALIDATION_ERROR","message":"Input contains unsupported fields.","details":{"fields":["tariff_myr_per_kwh"]}}
```

The same input without the tariff field resolves to a default average tariff of **0.386 MYR/kWh**, derived from the bundled residential tier fixture at 600 kWh. A Host that knows the real tariff cannot supply it, and every downstream savings and payback figure inherits the default.

### E2: Both consumption inputs produce a value matching neither

| Input | `estimated_monthly_kwh` | Tariff |
| --- | --- | --- |
| `monthly_kwh: 600` | 600 | 0.386 |
| `monthly_bill_myr: 300` | 745.7 | 0.402 |
| both, `600` and `300` | **776.5** | 0.386 |

The combined case is not a precedence choice between two interpretations. The implementation uses the user's 600 kWh to select the tiered tariff, then discards the 600 and recomputes consumption as `bill / tariff`. The result agrees with neither input, and nothing in the response marks that the user's stated consumption was overridden.

### E3: Precedence is inconsistent across `customer_type`

With `monthly_kwh: 600` and `monthly_bill_myr: 300`:

- `residential` → 776.5 kWh. The stated consumption is discarded.
- `commercial` → 600 kWh. The stated consumption is honoured.

One contract, two precedence behaviours, neither documented.

### E4: Non-residential bill conversion uses the residential fallback

With `customer_type: "commercial"` and `monthly_bill_myr: 300` only, consumption is derived as `300 / 0.45` using the **residential** fallback tariff, giving 666.7 kWh, while savings are computed at the non-residential tariff of 0.5. The implied bill is `666.7 × 0.5 = RM333`, contradicting the RM300 the user supplied.

E3 and E4 were found while reproducing the reported issues. They are not in the original report.

### E5: Investment scope is unmarked in `financial`

With `need_backup: true`, storage is sized at 6.5 kWh / 3.0 kW, and `financial.estimated_investment_myr` is **15750.0** — identical to the same request without backup. The caveat exists, but only as the last string in `recommended_config.notes`. Nothing inside the `financial` object marks its scope, so a Host reading `financial` alone will present a PV-only figure as the system investment.

## Proposed Changes

### C1: Optional `tariff_myr_per_kwh` input

Add to the input schema:

```json
"tariff_myr_per_kwh": {
  "type": "number",
  "exclusiveMinimum": 0,
  "maximum": 10,
  "description": "Optional user-supplied average electricity tariff in MYR per kWh. When provided it overrides bundled default tariff data."
}
```

Compatibility（兼容性）: additive and optional. Existing callers are unaffected. Permitted by the Accepted contract's compatibility note.

The upper bound is a validation guard against absurd or mistyped values, not a business limit.

### C2: Deterministic tariff resolution with declared source

Resolution order:

1. If `tariff_myr_per_kwh` is provided, use it.
2. Otherwise, for `residential`, use the tiered fixture average computed at the resolved consumption.
3. Otherwise, use the non-residential fixture tariff.

Add to the success output:

```json
"tariff_source": {
  "type": "string",
  "enum": ["user_provided", "default_residential_tiered", "default_non_residential"]
}
```

`estimated_avg_tariff_myr_per_kwh` keeps its meaning and always reports the tariff actually used.

### C3: Explicit consumption precedence with consistency validation

Replace the undocumented behaviour with a stated rule:

1. When `monthly_kwh` is provided, it is authoritative. Direct consumption measurement is never overridden by a derived value.
2. When only `monthly_bill_myr` is provided, derive consumption as `bill / resolved_tariff`, using the tariff for the requested `customer_type`. This closes E4.
3. When both are provided, validate consistency: compare `monthly_bill_myr` against `monthly_kwh × resolved_tariff`.
   - Within tolerance: proceed on `monthly_kwh` and report the reconciliation in output.
   - Outside tolerance: return an error rather than silently choosing one input.

Add to the success output:

```json
"consumption_source": {
  "type": "string",
  "enum": ["monthly_kwh", "derived_from_bill"]
}
```

Add one error code to the error enum:

```text
INCONSISTENT_CONSUMPTION_INPUT
```

with `details` carrying the supplied bill, the implied bill, the resolved tariff, and the tolerance applied, so a Host can explain the mismatch or retry with one input.

**Approved parameter（已批准参数）**: the tolerance band is **±10%**, accepted by Human Decision on 2026-08-29. Boundary values must be tested. Rationale as proposed: wide enough to absorb tiered-tariff rounding and a partial billing period, narrow enough to catch a genuine contradiction. The E2 case, RM300 against 600 kWh at 0.386 implying RM231.6, is a 23% mismatch and correctly errors.

**Approved choice（已批准选择）**: an out-of-tolerance mismatch returns an **error**, accepted by Human Decision on 2026-08-29. Downgrading to a warning is forbidden. Silently continuing is the exact failure this amendment exists to remove, and a warning inside a success payload is easy for a Host to ignore. The cost is that a previously-successful call can now fail, which is the breaking change recorded below.

### C4: Explicit PV-only investment scope

Add to `financial`:

```json
"investment_scope": { "type": "string", "enum": ["pv_only"] }
```

and state in the field description that `estimated_investment_myr` excludes storage, installation variance, and grid connection cost.

Storage pricing is **not** implemented. `storage_recommended: true` with `investment_scope: "pv_only"` is the honest representation of the current Core v0 limitation. The existing note in `recommended_config.notes` is retained.

## Compatibility Impact

| Change | Kind | Impact |
| --- | --- | --- |
| C1 optional input | Additive | None for existing callers. |
| C2 `tariff_source` output | Additive property | Breaks consumers validating strictly against the current `additionalProperties: false` output schema. |
| C3 `consumption_source` output | Additive property | Same as above. |
| C3 precedence change | **Semantic, breaking** | Residential callers supplying both inputs receive different numbers. This is the defect being corrected, but it is an observable behaviour change. |
| C3 new error code | Additive enum value | A previously-successful call with contradictory inputs now returns an error. |
| C4 `investment_scope` | Additive property | Same strict-validation impact as above. |

Because the success output declares `additionalProperties: false`, **no output field can be added without a version bump**. This amendment therefore proposes Core v0.2 rather than an in-place edit, and the contract must state that v0.1 consumers validating strictly will reject v0.2 responses.

No field is removed or renamed, so ADR review is not triggered on that basis.

## Out Of Scope

- Storage pricing and storage-inclusive investment.
- Any new tool. The inventory stays at one public tool.
- Provider, OCR, LLM, database, CRM, and Lead capability.
- Remote HTTP transport and authentication.
- Location-specific tariff logic. `location` remains metadata.
- Changing the bundled fixture values.

## Validation Plan

Required before the amendment can be marked implemented:

- Unit tests for tariff resolution across all three `tariff_source` values.
- Unit tests for the three consumption paths and for the tolerance boundary, including just inside and just outside.
- Regression tests reproducing E1 through E5, each failing before the fix and passing after.
- A test asserting `financial.investment_scope` is present whenever storage is recommended.
- MCP runtime discovery test confirming the published input and output schemas match this amendment, since discovery-time schema fidelity has previously diverged from the accepted contract.
- Full stdio Host round-trip through a real client session.

## Documentation Impact

- `docs/contracts/mcp-tools.md` gains the v0.2 schemas, the resolution rules, the new error code, and a compatibility note. Not edited until approved.
- README example arguments and the tool description gain the optional tariff field.
- `docs/data/fixtures.md` clarifies that fixture tariffs are defaults, overridable per call.
- Project Context and System Map need no change; boundaries are unchanged.

## Interaction With The Open Release Gate

`PLAN-0002` Release Preparation is blocked at a Human Gate on `ADR-0002` D4, and the repository still has no commits. This amendment does not unblock or alter that gate. If approved, it adds contract, code, test, and documentation changes that must pass the same Release Safety Gate before any first tracked baseline.

## Ready To Enter PLAN

Yes.

Reason（原因）: All four changes are Accepted, both open parameters are decided, and the ADR boundary question was ruled on by the project owner. Implementation proceeds under `docs/plan/PLAN-0003-contract-v0-2-implementation.md`.
