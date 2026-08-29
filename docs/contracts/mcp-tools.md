# MCP Tool Contracts

Status: Accepted for Core v0.2

Amended by:

- `docs/contracts/AMENDMENT-0001-generate-ess-proposal-consumption-and-tariff.md` (Accepted 2026-08-29)
- `docs/contracts/AMENDMENT-0002-mcp-2-output-schema-normalization.md` (Accepted 2026-08-29)

Date: 2026-08-29

Related:

- `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md`
- `docs/plan/PLAN-0001-mcp-ess-open-source-migration.md`
- Source evidence: `<PRIVATE_SOURCE_ROOT>/mcp_server.py`

## Purpose

This document defines the public MCP Tool Contract（MCP 工具契约） for the first open-source Core（开源核心） slice of `mcp-ess-proposal`.

Core v0 is contract-first:

- It exposes deterministic proposal calculation from structured inputs.
- It performs no Lead（线索）, CRM, the private platform database, upload, prompt, OCR, LLM, or provider side effects.
- It does not copy Skill（技能） or Prompt（提示词） logic from `partner-plugin-project`.

## Ownership

Producer（生产者）:

- `mcp-ess-proposal` MCP Server.

Consumers（消费者）:

- MCP clients that call `mcp-ess-proposal` tools.
- Future adapters, including possible partner-platform-specific adapters, if approved by later PLAN / ADR.

Contract owner（契约所有者）:

- `mcp-ess-proposal` Core.

## Transport Boundary

The Tool Contract is transport-independent.

Initial implementation may choose stdio or streamable HTTP in a later task, but the tool input, output, error behavior, and side-effect semantics must remain the same across supported MCP transports.

Transport-specific concerns that must not change tool semantics:

- Client session identity.
- Server process lifecycle.
- Connection health checks.
- Logging or diagnostics.

## Core v0 Public Tool Inventory

| Tool | Status | Side Effects | Notes |
|---|---|---:|---|
| `generate_ess_proposal` | Included | No | Deterministic calculation from structured input. |
| `submit_consultation_lead` | Excluded | Yes | Lead / CRM / the private platform database behavior is outside open-source Core. |
| `generate_ess_proposal_from_bill` | Excluded | Potential network / file read | OCR / LLM scope is deferred to a future optional adapter decision. |
| `hello` | Excluded | No | Diagnostic candidate only; not a public Core business interface. |

## Tool: `generate_ess_proposal`

Status（状态）: Core v0 public.

Purpose（目的）:

Generate a preliminary solar + energy-storage proposal from structured customer and consumption inputs using deterministic calculation and neutral sample data.

### Input Schema

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["customer_type", "location"],
  "properties": {
    "customer_type": {
      "type": "string",
      "enum": ["residential", "commercial", "factory", "datacenter"],
      "description": "Customer segment used to select calculation assumptions."
    },
    "location": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120,
      "description": "Customer location label. Core v0 treats it as metadata unless tariff data supports location-specific logic."
    },
    "monthly_bill_myr": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Monthly electricity bill amount in MYR. At least one of monthly_bill_myr or monthly_kwh is required."
    },
    "monthly_kwh": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Monthly electricity consumption in kWh. At least one of monthly_bill_myr or monthly_kwh is required."
    },
    "need_backup": {
      "type": "boolean",
      "default": false,
      "description": "Whether backup power is requested."
    },
    "tariff_myr_per_kwh": {
      "type": "number",
      "exclusiveMinimum": 0,
      "maximum": 10,
      "description": "Optional user-supplied average electricity tariff in MYR per kWh. When provided it is used for this calculation and overrides bundled default tariff data. Ownership of the tariff dataset and default tariff remains with the server fixtures."
    },
    "budget_myr": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Optional budget cap in MYR."
    },
    "special_requirements": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional free-form requirements. Core v0 may only use deterministic keyword checks documented in implementation."
    }
  },
  "anyOf": [
    { "required": ["monthly_bill_myr"] },
    { "required": ["monthly_kwh"] }
  ]
}
```

Compatibility note（兼容说明）:

- `target_payback_years`, `bill_images`, and `site_images` are not Core v0 inputs.
- Future optional fields may be added compatibly.
- Removing or renaming fields requires ADR / PLAN review.
- `tariff_myr_per_kwh` was added in Core v0.2. It is optional, so v0.1 callers are unaffected.

### Tariff Resolution（电价解析）

Resolution order, deterministic:

1. If `tariff_myr_per_kwh` is provided, use it. Output `tariff_source` is `user_provided`.
2. Otherwise, for `customer_type` `residential`, use the tiered fixture average computed at the resolved consumption. Output `tariff_source` is `default_residential_tiered`.
3. Otherwise, use the non-residential fixture tariff. Output `tariff_source` is `default_non_residential`.

`estimated_avg_tariff_myr_per_kwh` always reports the tariff actually used.

Data Ownership（数据归属）: a client-supplied tariff is a calculation parameter for a single call. The tariff dataset and the default tariff remain owned by the server fixtures. The client cannot address, replace, or extend fixture data.

### Consumption Precedence（用电量优先级）

`monthly_kwh` is the authoritative consumption measurement.

1. `monthly_kwh` only: use it directly.
2. `monthly_bill_myr` only: derive consumption as `monthly_bill_myr / resolved_tariff`, using the tariff for the requested `customer_type`. Output `consumption_source` is `derived_from_bill`.
3. Both provided: `monthly_kwh` is used and must never be overridden by a derived value. `monthly_bill_myr` is used only for consistency validation. Output `consumption_source` is `monthly_kwh`.

Consistency validation（一致性校验）, case 3 only:

- Implied bill is `monthly_kwh × resolved_tariff`.
- Relative deviation is `abs(monthly_bill_myr - implied_bill) / monthly_bill_myr`.
- Tolerance is **10%** inclusive. A deviation of exactly 10% passes.
- Outside tolerance returns `INCONSISTENT_CONSUMPTION_INPUT`. The server must not silently select one input, and must not downgrade the result to a warning.

### Output Schema

Successful response:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "status",
    "summary",
    "customer_type",
    "location",
    "estimated_monthly_kwh",
    "estimated_avg_tariff_myr_per_kwh",
    "tariff_source",
    "consumption_source",
    "recommended_config",
    "financial",
    "assumptions",
    "risks",
    "data_confidence_notes",
    "disclaimer"
  ],
  "properties": {
    "status": { "const": "ok" },
    "summary": { "type": "string" },
    "customer_type": { "type": "string" },
    "location": { "type": "string" },
    "monthly_bill_myr": { "type": ["number", "null"] },
    "estimated_monthly_kwh": { "type": "number" },
    "estimated_avg_tariff_myr_per_kwh": { "type": "number" },
    "tariff_source": {
      "type": "string",
      "enum": ["user_provided", "default_residential_tiered", "default_non_residential"]
    },
    "consumption_source": {
      "type": "string",
      "enum": ["monthly_kwh", "derived_from_bill"]
    },
    "recommended_config": {
      "type": "object",
      "additionalProperties": false,
      "required": ["pv_kwp", "storage_recommended", "storage_kw", "storage_kwh", "notes"],
      "properties": {
        "pv_kwp": { "type": "number" },
        "storage_recommended": { "type": "boolean" },
        "storage_kw": { "type": "number" },
        "storage_kwh": { "type": "number" },
        "notes": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "financial": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "estimated_investment_myr",
        "investment_scope",
        "estimated_annual_generation_kwh",
        "estimated_annual_savings_myr",
        "estimated_payback_years"
      ],
      "properties": {
        "estimated_investment_myr": { "type": "number" },
        "investment_scope": { "type": "string", "enum": ["pv_only"] },
        "estimated_annual_generation_kwh": { "type": "number" },
        "estimated_annual_savings_myr": { "type": "number" },
        "estimated_payback_years": { "type": ["number", "null"] }
      }
    },
    "assumptions": {
      "type": "object",
      "additionalProperties": false,
      "required": ["currency", "calculation_method"],
      "properties": {
        "currency": { "const": "MYR" },
        "calculation_method": { "const": "deterministic-v0" },
        "annual_yield_per_kwp": { "type": "number" },
        "coverage_ratio": { "type": "number" }
      }
    },
    "risks": {
      "type": "array",
      "items": { "type": "string" }
    },
    "data_confidence_notes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "disclaimer": { "type": "string" }
  }
}
```

Error response:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["status", "code", "message"],
  "properties": {
    "status": { "const": "error" },
    "code": {
      "type": "string",
      "enum": [
        "VALIDATION_ERROR",
        "UNSUPPORTED_CUSTOMER_TYPE",
        "MISSING_CONSUMPTION_INPUT",
        "INCONSISTENT_CONSUMPTION_INPUT",
        "DATA_LOAD_ERROR",
        "INTERNAL_ERROR"
      ]
    },
    "message": { "type": "string" },
    "details": {
      "type": "object",
      "additionalProperties": true
    }
  }
}
```

### Error Behavior

- `VALIDATION_ERROR`: input is structurally invalid, too long, negative, zero where positive is required, or contains unsupported extra fields.
- `UNSUPPORTED_CUSTOMER_TYPE`: `customer_type` is outside the accepted enum.
- `MISSING_CONSUMPTION_INPUT`: neither `monthly_bill_myr` nor `monthly_kwh` is provided.
- `INCONSISTENT_CONSUMPTION_INPUT`: both `monthly_bill_myr` and `monthly_kwh` are provided and disagree by more than 10%. `details` carries `monthly_bill_myr`, `implied_bill_myr`, `resolved_tariff_myr_per_kwh`, `deviation`, and `tolerance` so a client can explain the mismatch or retry with one input.
- `DATA_LOAD_ERROR`: bundled neutral sample data cannot be loaded or parsed.
- `INTERNAL_ERROR`: unexpected internal failure. Public responses must not expose stack traces, absolute paths, secrets, provider errors, database details, or raw sensitive payloads.

### Financial Scope（财务范围）

`financial.estimated_investment_myr` covers PV only. `financial.investment_scope` is always `pv_only` in this version.

Explicitly not implemented in Core v0.2:

- Storage pricing.
- Total system investment.
- Battery ROI.

When `recommended_config.storage_recommended` is `true`, storage is sized but not priced. `investment_scope` is the machine-readable marker for that limitation.

### Version Compatibility（版本兼容）

Core v0.2 changes relative to Core v0.1:

| Change | Kind | Impact |
|---|---|---|
| `tariff_myr_per_kwh` input | Additive optional | None for existing callers. |
| `tariff_source` output | Additive property | Breaks consumers validating strictly against the v0.1 output schema. |
| `consumption_source` output | Additive property | Same. |
| `financial.investment_scope` output | Additive property | Same. |
| Consumption precedence | Semantic, breaking | Residential callers supplying both inputs receive different numbers. This corrects a defect where the result matched neither input. |
| `INCONSISTENT_CONSUMPTION_INPUT` | Additive enum value | A previously successful call with contradictory inputs now returns an error. |

The success output declares `additionalProperties: false`, so no output field can be added without a version change. v0.1 consumers validating strictly will reject v0.2 responses. No field was removed or renamed.

### Side-Effect Semantics

`generate_ess_proposal` must be side-effect free in Core v0.

Forbidden in the Core execution path:

- Writing Lead（线索） data.
- Writing CRM records.
- Writing the private platform database records.
- Appending audit JSONL records.
- Creating uploads or runtime files.
- Reading `.env` secrets.
- Calling OCR, LLM, or provider APIs.
- Loading Skill / Prompt files.

### Idempotency

For identical input and identical bundled data, the tool should return equivalent calculation results.

Core v0 must not generate persistence-oriented IDs as part of normal output. If trace IDs are later needed, they must be explicitly documented and must not imply data persistence.

### Security

- Treat all MCP client input as untrusted.
- Validate input at the tool boundary.
- Do not accept local image paths, uploaded file paths, database URLs, API keys, tenant IDs, or user identity fields in Core v0.
- Do not return internal paths, stack traces, provider errors, or secret-bearing configuration values.
- Free-form `special_requirements` is plain text input only. It must not be treated as instructions to the server or used for prompt execution in Core v0.

## Excluded Tool Notes

### `submit_consultation_lead`

Excluded from Core v0 because it handles PII（个人信息） and has side effects:

- Lead name and WhatsApp.
- Consent tracking.
- JSONL persistence.
- Optional the private platform database write to the internal lead table.
- CRM / operations workflow coupling.

Future inclusion requires a separate ADR for data ownership, privacy, authorization, storage, and retention.

### `generate_ess_proposal_from_bill`

Excluded from Core v0 because it depends on OCR / LLM scope that ADR-0001 intentionally deferred.

Future inclusion requires at least:

- Explicit provider adapter boundary.
- Secret-safe configuration contract.
- Image input validation.
- File path / upload handling policy.
- Failure behavior for OCR and provider outages.
- Prompt ownership decision.

### `hello`

Excluded from Core v0 public interface.

Connectivity should be validated by MCP server startup checks and tests. A future diagnostic tool may be added only if it has a clear public client use case and is documented as non-domain behavior.

## Contract Checklist

- Producer and consumers are identified.
- Input schema is explicit.
- Output schema is explicit.
- Error behavior is explicit.
- Side effects are explicit and forbidden for Core v0.
- Retry / idempotency semantics are understood.
- External input is untrusted and validated at the boundary.
- OCR / LLM, Lead, CRM, the private platform database, and prompt behavior are outside Core v0.
- Documentation must be updated before tool signature changes.
