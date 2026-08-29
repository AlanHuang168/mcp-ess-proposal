# Data Fixtures

Status: Core v0

Date: 2026-08-29

## Purpose

Core v0 uses neutral Data Fixtures（数据样例） to validate deterministic proposal calculations without private brand, CRM, lead, database, provider, OCR, LLM, prompt, upload, or runtime coupling.

## Files

- `src/mcp_ess_proposal/fixtures/calculation-defaults.json`
- `src/mcp_ess_proposal/fixtures/sample-products.json`

## Ownership

The fixtures are owned by `mcp-ess-proposal` Core（核心）.

They are not official tariffs, quotations, product specifications, or investment advice.

## Compatibility

`calculation-defaults.json` feeds `CalculationData` and must preserve these fields until a later accepted contract or plan changes the calculator:

- `residential_tiers`
- `fallback_residential_tariff`
- `fallback_non_residential_tariff`
- `annual_yield_per_kwp`
- `coverage_ratio`
- `min_kwp`
- `max_kwp`
- `cost_per_kwp_myr`
- `default_storage_hours`
- `disclaimer`
- `data_confidence_notes`

`sample-products.json` is a neutral fixture for future data validation. Core v0 calculation does not depend on product selection.

## Tariff Override（电价覆盖）

Since Core v0.2, a client may supply `tariff_myr_per_kwh` to override the bundled tariff for a single calculation. The successful response reports `tariff_source` so a consumer can tell whether the tariff came from the caller or from these fixtures.

Data Ownership（数据归属） is unchanged: the tariff dataset and the default tariff remain owned by these server-side fixtures. A client-supplied tariff is a calculation parameter for one call. Clients cannot address, replace, or extend fixture data.
