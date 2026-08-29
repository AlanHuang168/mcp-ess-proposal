from __future__ import annotations

from dataclasses import fields
from typing import Any

from .data import DEFAULT_CALCULATION_DATA, CalculationData
from .models import (
    CalculationAssumptions,
    ErrorOutput,
    FinancialEstimate,
    ProposalInput,
    ProposalOutput,
    RecommendedConfig,
)

SUPPORTED_CUSTOMER_TYPES = {"residential", "commercial", "factory", "datacenter"}
MAX_TARIFF_MYR_PER_KWH = 10
CONSISTENCY_TOLERANCE = 0.10
_TOLERANCE_EPSILON = 1e-9
BACKUP_KEYWORDS = ("backup", "battery", "storage", "ess")
INPUT_FIELDS = {field.name for field in fields(ProposalInput)}


def generate_ess_proposal(
    payload: ProposalInput | dict[str, Any],
    data: CalculationData = DEFAULT_CALCULATION_DATA,
) -> dict[str, Any]:
    input_data, error = _coerce_input(payload)
    if error:
        return error.to_dict()

    assert input_data is not None
    error = _validate_input(input_data)
    if error:
        return error.to_dict()

    try:
        return _calculate(input_data, data).to_dict()
    except Exception:
        return ErrorOutput(
            status="error",
            code="INTERNAL_ERROR",
            message="Proposal calculation failed unexpectedly.",
        ).to_dict()


def estimate_residential_avg_tariff(monthly_kwh: float, data: CalculationData) -> float:
    if monthly_kwh <= 0:
        return data.fallback_residential_tariff

    remaining = monthly_kwh
    total_cost = 0.0
    previous_upto = 0.0

    for tier in data.residential_tiers:
        if tier.upto_kwh is None:
            total_cost += remaining * tier.rate_myr_per_kwh
            break

        band = tier.upto_kwh - previous_upto
        if remaining <= band:
            total_cost += remaining * tier.rate_myr_per_kwh
            remaining = 0
            break

        total_cost += band * tier.rate_myr_per_kwh
        remaining -= band
        previous_upto = tier.upto_kwh

    return total_cost / monthly_kwh if monthly_kwh > 0 else data.fallback_residential_tariff


def _coerce_input(payload: ProposalInput | dict[str, Any]) -> tuple[ProposalInput | None, ErrorOutput | None]:
    if isinstance(payload, ProposalInput):
        return payload, None

    if not isinstance(payload, dict):
        return None, ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="Input must be an object.",
        )

    extra_fields = sorted(set(payload) - INPUT_FIELDS)
    if extra_fields:
        return None, ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="Input contains unsupported fields.",
            details={"fields": extra_fields},
        )

    try:
        return ProposalInput(**payload), None
    except TypeError as exc:
        return None, ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="Input does not match the proposal schema.",
            details={"error": str(exc)},
        )


def _validate_input(input_data: ProposalInput) -> ErrorOutput | None:
    if input_data.customer_type not in SUPPORTED_CUSTOMER_TYPES:
        return ErrorOutput(
            status="error",
            code="UNSUPPORTED_CUSTOMER_TYPE",
            message="Unsupported customer_type.",
            details={"allowed": sorted(SUPPORTED_CUSTOMER_TYPES)},
        )

    if not isinstance(input_data.location, str) or not input_data.location.strip():
        return ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="location is required.",
        )

    if len(input_data.location) > 120:
        return ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="location exceeds 120 characters.",
        )

    if input_data.monthly_bill_myr is None and input_data.monthly_kwh is None:
        return ErrorOutput(
            status="error",
            code="MISSING_CONSUMPTION_INPUT",
            message="Provide at least one of monthly_bill_myr or monthly_kwh.",
        )

    if not isinstance(input_data.need_backup, bool):
        return ErrorOutput(
            status="error",
            code="VALIDATION_ERROR",
            message="need_backup must be a boolean.",
        )

    if input_data.tariff_myr_per_kwh is not None:
        if not _is_positive_number(input_data.tariff_myr_per_kwh):
            return ErrorOutput(
                status="error",
                code="VALIDATION_ERROR",
                message="tariff_myr_per_kwh must be a positive number when provided.",
            )
        if input_data.tariff_myr_per_kwh > MAX_TARIFF_MYR_PER_KWH:
            return ErrorOutput(
                status="error",
                code="VALIDATION_ERROR",
                message=f"tariff_myr_per_kwh must not exceed {MAX_TARIFF_MYR_PER_KWH}.",
            )

    for name in ("monthly_bill_myr", "monthly_kwh", "budget_myr"):
        value = getattr(input_data, name)
        if value is not None and not _is_positive_number(value):
            return ErrorOutput(
                status="error",
                code="VALIDATION_ERROR",
                message=f"{name} must be a positive number when provided.",
            )

    if input_data.special_requirements is not None:
        if not isinstance(input_data.special_requirements, str):
            return ErrorOutput(
                status="error",
                code="VALIDATION_ERROR",
                message="special_requirements must be a string.",
            )
        if len(input_data.special_requirements) > 2000:
            return ErrorOutput(
                status="error",
                code="VALIDATION_ERROR",
                message="special_requirements exceeds 2000 characters.",
            )

    return None


def _calculate(input_data: ProposalInput, data: CalculationData) -> ProposalOutput | ErrorOutput:
    resolution = _resolve_consumption(input_data, data)
    if isinstance(resolution, ErrorOutput):
        return resolution
    monthly_kwh, avg_tariff, tariff_source, consumption_source = resolution
    annual_kwh = monthly_kwh * 12
    recommended_kwp = _round_half((annual_kwh * data.coverage_ratio) / data.annual_yield_per_kwp)
    recommended_kwp = max(data.min_kwp, min(data.max_kwp, recommended_kwp))

    if input_data.budget_myr:
        budget_limited_kwp = _round_half(input_data.budget_myr / data.cost_per_kwp_myr)
        recommended_kwp = max(data.min_kwp, min(recommended_kwp, budget_limited_kwp))

    storage_recommended = _wants_backup(input_data)
    storage_kwh = _round_half(recommended_kwp * data.default_storage_hours) if storage_recommended else 0
    storage_kw = _round_half(storage_kwh / 2) if storage_kwh else 0

    annual_generation = recommended_kwp * data.annual_yield_per_kwp
    annual_savings = annual_generation * avg_tariff
    investment = recommended_kwp * data.cost_per_kwp_myr
    payback = round(investment / annual_savings, 1) if annual_savings > 0 else None

    notes = [
        f"PV sizing covers about {data.coverage_ratio:.0%} of estimated annual consumption.",
        "Storage sizing is included only when backup or storage is explicitly requested.",
    ]
    risks = [
        "Actual generation depends on site conditions, roof area, shading, and local grid rules.",
        "Tariff and cost assumptions are sample values and must be verified before a formal proposal.",
    ]
    if storage_recommended:
        notes.append("Storage investment is not included in Core v0 financial estimates.")

    return ProposalOutput(
        status="ok",
        summary=(
            f"Preliminary deterministic estimate for {input_data.customer_type} in "
            f"{input_data.location}: {recommended_kwp:g} kWp PV"
            f"{f' with {storage_kwh:g} kWh storage' if storage_recommended else ''}, "
            f"estimated annual savings RM {round(annual_savings):,.0f}."
        ),
        customer_type=input_data.customer_type,
        location=input_data.location.strip(),
        monthly_bill_myr=_round_money(input_data.monthly_bill_myr) if input_data.monthly_bill_myr else None,
        estimated_monthly_kwh=round(monthly_kwh, 1),
        estimated_avg_tariff_myr_per_kwh=round(avg_tariff, 3),
        tariff_source=tariff_source,
        consumption_source=consumption_source,
        recommended_config=RecommendedConfig(
            pv_kwp=recommended_kwp,
            storage_recommended=storage_recommended,
            storage_kw=storage_kw,
            storage_kwh=storage_kwh,
            notes=notes,
        ),
        financial=FinancialEstimate(
            estimated_investment_myr=round(investment, 0),
            investment_scope="pv_only",
            estimated_annual_generation_kwh=round(annual_generation, 0),
            estimated_annual_savings_myr=round(annual_savings, 0),
            estimated_payback_years=payback,
        ),
        assumptions=CalculationAssumptions(
            annual_yield_per_kwp=data.annual_yield_per_kwp,
            coverage_ratio=data.coverage_ratio,
        ),
        risks=risks,
        data_confidence_notes=list(data.data_confidence_notes),
        disclaimer=data.disclaimer,
    )


def _resolve_consumption(
    input_data: ProposalInput, data: CalculationData
) -> tuple[float, float, str, str] | ErrorOutput:
    """Resolve consumption and tariff per the Core v0.2 contract.

    monthly_kwh is the authoritative consumption measurement and is never
    overridden by a value derived from the bill. When both inputs are present the
    bill is used only for consistency validation.
    """
    user_tariff = input_data.tariff_myr_per_kwh

    if input_data.monthly_kwh:
        monthly_kwh = input_data.monthly_kwh
        consumption_source = "monthly_kwh"
        avg_tariff, tariff_source = _resolve_tariff(user_tariff, input_data.customer_type, monthly_kwh, data)

        if input_data.monthly_bill_myr:
            error = _validate_consistency(input_data.monthly_bill_myr, monthly_kwh, avg_tariff)
            if error:
                return error
    else:
        consumption_source = "derived_from_bill"
        bill = input_data.monthly_bill_myr

        if user_tariff:
            avg_tariff, tariff_source = user_tariff, "user_provided"
        elif input_data.customer_type == "residential":
            # The tiered tariff depends on consumption, so approximate consumption
            # with the residential fallback first, then resolve the tiered tariff.
            approx_kwh = bill / data.fallback_residential_tariff
            avg_tariff = estimate_residential_avg_tariff(approx_kwh, data)
            tariff_source = "default_residential_tiered"
        else:
            avg_tariff = data.fallback_non_residential_tariff
            tariff_source = "default_non_residential"

        monthly_kwh = bill / avg_tariff

    return monthly_kwh, avg_tariff, tariff_source, consumption_source


def _resolve_tariff(
    user_tariff: float | None, customer_type: str, monthly_kwh: float, data: CalculationData
) -> tuple[float, str]:
    if user_tariff:
        return user_tariff, "user_provided"
    if customer_type == "residential":
        return estimate_residential_avg_tariff(monthly_kwh, data), "default_residential_tiered"
    return data.fallback_non_residential_tariff, "default_non_residential"


def _validate_consistency(bill: float, monthly_kwh: float, avg_tariff: float) -> ErrorOutput | None:
    implied_bill = monthly_kwh * avg_tariff
    deviation = abs(bill - implied_bill) / bill

    if deviation > CONSISTENCY_TOLERANCE + _TOLERANCE_EPSILON:
        return ErrorOutput(
            status="error",
            code="INCONSISTENT_CONSUMPTION_INPUT",
            message=(
                "monthly_bill_myr and monthly_kwh disagree by more than "
                f"{CONSISTENCY_TOLERANCE:.0%}. Provide only one, or correct the inputs."
            ),
            details={
                "monthly_bill_myr": round(bill, 2),
                "implied_bill_myr": round(implied_bill, 2),
                "resolved_tariff_myr_per_kwh": round(avg_tariff, 3),
                "deviation": round(deviation, 4),
                "tolerance": CONSISTENCY_TOLERANCE,
            },
        )
    return None


def _wants_backup(input_data: ProposalInput) -> bool:
    if input_data.need_backup:
        return True
    special = (input_data.special_requirements or "").lower()
    return any(keyword in special for keyword in BACKUP_KEYWORDS)


def _round_half(value: float) -> float:
    return round(value * 2) / 2


def _round_money(value: float | None) -> float | None:
    return round(value, 2) if value is not None else None


def _is_positive_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float) and value > 0
