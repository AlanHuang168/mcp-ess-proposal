from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

CustomerType = Literal["residential", "commercial", "factory", "datacenter"]


@dataclass(frozen=True)
class ProposalInput:
    customer_type: CustomerType
    location: str
    monthly_bill_myr: float | None = None
    monthly_kwh: float | None = None
    tariff_myr_per_kwh: float | None = None
    need_backup: bool = False
    budget_myr: float | None = None
    special_requirements: str | None = None


@dataclass(frozen=True)
class RecommendedConfig:
    pv_kwp: float
    storage_recommended: bool
    storage_kw: float
    storage_kwh: float
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FinancialEstimate:
    estimated_investment_myr: float
    investment_scope: Literal["pv_only"]
    estimated_annual_generation_kwh: float
    estimated_annual_savings_myr: float
    estimated_payback_years: float | None


@dataclass(frozen=True)
class CalculationAssumptions:
    currency: str = "MYR"
    calculation_method: str = "deterministic-v0"
    annual_yield_per_kwp: float = 0
    coverage_ratio: float = 0


@dataclass(frozen=True)
class ProposalOutput:
    status: Literal["ok"]
    summary: str
    customer_type: str
    location: str
    monthly_bill_myr: float | None
    estimated_monthly_kwh: float
    estimated_avg_tariff_myr_per_kwh: float
    tariff_source: Literal["user_provided", "default_residential_tiered", "default_non_residential"]
    consumption_source: Literal["monthly_kwh", "derived_from_bill"]
    recommended_config: RecommendedConfig
    financial: FinancialEstimate
    assumptions: CalculationAssumptions
    risks: list[str]
    data_confidence_notes: list[str]
    disclaimer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ErrorOutput:
    status: Literal["error"]
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
