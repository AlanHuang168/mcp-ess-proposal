from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib.resources import files
from typing import Any


@dataclass(frozen=True)
class TariffTier:
    upto_kwh: float | None
    rate_myr_per_kwh: float


@dataclass(frozen=True)
class CalculationData:
    residential_tiers: tuple[TariffTier, ...] = (
        TariffTier(200, 0.218),
        TariffTier(300, 0.334),
        TariffTier(600, 0.516),
        TariffTier(900, 0.546),
        TariffTier(None, 0.571),
    )
    fallback_residential_tariff: float = 0.45
    fallback_non_residential_tariff: float = 0.50
    annual_yield_per_kwp: float = 1350
    coverage_ratio: float = 0.70
    min_kwp: float = 3.0
    max_kwp: float = 15.0
    cost_per_kwp_myr: float = 4500
    default_storage_hours: float = 1.8
    disclaimer: str = (
        "This result is a preliminary deterministic estimate for planning only. "
        "It is not a formal quotation, investment advice, or utility tariff guarantee."
    )
    data_confidence_notes: tuple[str, ...] = field(
        default=(
            "Default tariff and cost assumptions are neutral sample values for validation.",
        )
    )


def load_default_calculation_data() -> CalculationData:
    raw = _load_json_fixture("calculation-defaults.json")
    return CalculationData(
        residential_tiers=tuple(
            TariffTier(
                upto_kwh=tier["upto_kwh"],
                rate_myr_per_kwh=tier["rate_myr_per_kwh"],
            )
            for tier in raw["residential_tiers"]
        ),
        fallback_residential_tariff=raw["fallback_residential_tariff"],
        fallback_non_residential_tariff=raw["fallback_non_residential_tariff"],
        annual_yield_per_kwp=raw["annual_yield_per_kwp"],
        coverage_ratio=raw["coverage_ratio"],
        min_kwp=raw["min_kwp"],
        max_kwp=raw["max_kwp"],
        cost_per_kwp_myr=raw["cost_per_kwp_myr"],
        default_storage_hours=raw["default_storage_hours"],
        disclaimer=raw["disclaimer"],
        data_confidence_notes=tuple(raw["data_confidence_notes"]),
    )


def load_sample_products() -> list[dict[str, Any]]:
    raw = _load_json_fixture("sample-products.json")
    return list(raw["products"])


def _load_json_fixture(name: str) -> dict[str, Any]:
    fixture = files("mcp_ess_proposal").joinpath("fixtures", name)
    return json.loads(fixture.read_text(encoding="utf-8"))


DEFAULT_CALCULATION_DATA = load_default_calculation_data()
