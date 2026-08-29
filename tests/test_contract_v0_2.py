"""Regression tests for MCP Tool Contract Core v0.2 (AMENDMENT-0001).

Each E-numbered test reproduces a defect found by the Claude Code MCP Host
end-to-end run on 2026-08-29 and recorded as Contract Drift Evidence.
"""

from __future__ import annotations

import unittest

from mcp_ess_proposal.calculator import CONSISTENCY_TOLERANCE, generate_ess_proposal

BASE = {"customer_type": "residential", "location": "Selangor"}


def call(**overrides):
    return generate_ess_proposal({**BASE, **overrides})


class TestE1UserSuppliedTariff(unittest.TestCase):
    """E1: a user-supplied tariff was rejected as an unsupported field."""

    def test_tariff_is_accepted_and_used(self):
        result = call(monthly_kwh=600, tariff_myr_per_kwh=0.60)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["estimated_avg_tariff_myr_per_kwh"], 0.60)
        self.assertEqual(result["tariff_source"], "user_provided")

    def test_user_tariff_changes_financials(self):
        default = call(monthly_kwh=600)
        supplied = call(monthly_kwh=600, tariff_myr_per_kwh=0.60)
        self.assertEqual(default["tariff_source"], "default_residential_tiered")
        self.assertNotEqual(
            default["financial"]["estimated_annual_savings_myr"],
            supplied["financial"]["estimated_annual_savings_myr"],
        )

    def test_tariff_bounds(self):
        self.assertEqual(call(monthly_kwh=600, tariff_myr_per_kwh=10)["status"], "ok")
        for bad in (0, -1, 10.1, 999):
            result = call(monthly_kwh=600, tariff_myr_per_kwh=bad)
            self.assertEqual(result["status"], "error", bad)
            self.assertEqual(result["code"], "VALIDATION_ERROR", bad)

    def test_tariff_source_non_residential(self):
        result = generate_ess_proposal(
            {"customer_type": "commercial", "location": "Selangor", "monthly_kwh": 600}
        )
        self.assertEqual(result["tariff_source"], "default_non_residential")


class TestE2ConsumptionPrecedence(unittest.TestCase):
    """E2: both inputs produced a consumption value matching neither."""

    def test_monthly_kwh_is_authoritative(self):
        result = call(monthly_kwh=600, monthly_bill_myr=232)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["estimated_monthly_kwh"], 600)
        self.assertEqual(result["consumption_source"], "monthly_kwh")

    def test_kwh_only_and_bill_only_paths(self):
        self.assertEqual(call(monthly_kwh=600)["consumption_source"], "monthly_kwh")
        self.assertEqual(call(monthly_bill_myr=300)["consumption_source"], "derived_from_bill")

    def test_original_host_case_now_errors_instead_of_inventing_a_value(self):
        result = call(monthly_kwh=600, monthly_bill_myr=300)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "INCONSISTENT_CONSUMPTION_INPUT")
        self.assertNotIn("estimated_monthly_kwh", result)


class TestE3PrecedenceConsistentAcrossCustomerType(unittest.TestCase):
    """E3: residential and non-residential disagreed on precedence."""

    def test_all_customer_types_honour_monthly_kwh(self):
        for customer_type in ("residential", "commercial", "factory", "datacenter"):
            result = generate_ess_proposal(
                {
                    "customer_type": customer_type,
                    "location": "Selangor",
                    "monthly_kwh": 600,
                    "monthly_bill_myr": 240,
                    "tariff_myr_per_kwh": 0.40,
                }
            )
            self.assertEqual(result["status"], "ok", customer_type)
            self.assertEqual(result["estimated_monthly_kwh"], 600, customer_type)
            self.assertEqual(result["consumption_source"], "monthly_kwh", customer_type)


class TestE4NonResidentialBillConversion(unittest.TestCase):
    """E4: non-residential bill conversion used the residential fallback tariff."""

    def test_derived_consumption_is_self_consistent(self):
        result = generate_ess_proposal(
            {"customer_type": "commercial", "location": "Selangor", "monthly_bill_myr": 300}
        )
        self.assertEqual(result["status"], "ok")
        implied = result["estimated_monthly_kwh"] * result["estimated_avg_tariff_myr_per_kwh"]
        self.assertAlmostEqual(implied, 300, places=6)

    def test_residential_derived_consumption_is_self_consistent(self):
        """Residential uses a tiered tariff, so the reported figures are consistent
        only to display precision: consumption is rounded to 1 decimal and the
        tariff to 3. The internal calculation is exact; recomputing the bill from
        the rounded outputs is therefore accurate to well under one percent."""
        result = call(monthly_bill_myr=300)
        implied = result["estimated_monthly_kwh"] * result["estimated_avg_tariff_myr_per_kwh"]
        self.assertLess(abs(implied - 300) / 300, 0.005)


class TestE5InvestmentScope(unittest.TestCase):
    """E5: the financial investment figure carried no scope marker."""

    def test_investment_scope_is_always_present(self):
        self.assertEqual(call(monthly_kwh=600)["financial"]["investment_scope"], "pv_only")

    def test_investment_scope_present_when_storage_recommended(self):
        result = call(monthly_kwh=600, need_backup=True)
        self.assertTrue(result["recommended_config"]["storage_recommended"])
        self.assertGreater(result["recommended_config"]["storage_kwh"], 0)
        self.assertEqual(result["financial"]["investment_scope"], "pv_only")

    def test_storage_is_not_priced(self):
        without = call(monthly_kwh=600)
        with_storage = call(monthly_kwh=600, need_backup=True)
        self.assertEqual(
            without["financial"]["estimated_investment_myr"],
            with_storage["financial"]["estimated_investment_myr"],
        )


class TestConsistencyTolerance(unittest.TestCase):
    """Approved tolerance is 10%, inclusive. Deviation is relative to the supplied bill."""

    #: implied bill is exactly 0.9 x bill, i.e. deviation is exactly +10%
    EXACT_HIGH = {"monthly_kwh": 675.0, "tariff_myr_per_kwh": 0.40, "monthly_bill_myr": 300.0}
    #: implied bill is exactly 1.1 x bill, i.e. deviation is exactly -10%
    EXACT_LOW = {"monthly_kwh": 825.0, "tariff_myr_per_kwh": 0.40, "monthly_bill_myr": 300.0}

    def test_tolerance_constant_matches_approved_value(self):
        self.assertEqual(CONSISTENCY_TOLERANCE, 0.10)

    def test_exactly_at_tolerance_passes_both_directions(self):
        for label, payload in (("high", self.EXACT_HIGH), ("low", self.EXACT_LOW)):
            with self.subTest(label):
                self.assertEqual(call(**payload)["status"], "ok")

    def test_just_inside_tolerance_passes(self):
        self.assertEqual(
            call(monthly_kwh=600, tariff_myr_per_kwh=0.40, monthly_bill_myr=252.0)["status"],
            "ok",
        )

    def test_just_outside_tolerance_errors(self):
        for label, kwh, bill in (("high", 674.0, 300.0), ("low", 828.0, 300.0)):
            with self.subTest(label):
                result = call(monthly_kwh=kwh, tariff_myr_per_kwh=0.40, monthly_bill_myr=bill)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["code"], "INCONSISTENT_CONSUMPTION_INPUT")

    def test_error_details_are_actionable(self):
        result = call(monthly_kwh=600, monthly_bill_myr=300)
        details = result["details"]
        self.assertEqual(
            set(details),
            {
                "monthly_bill_myr",
                "implied_bill_myr",
                "resolved_tariff_myr_per_kwh",
                "deviation",
                "tolerance",
            },
        )
        self.assertEqual(details["tolerance"], CONSISTENCY_TOLERANCE)
        self.assertGreater(details["deviation"], CONSISTENCY_TOLERANCE)

    def test_no_silent_fallback_to_either_input(self):
        """The contract forbids silently selecting one input or warning instead."""
        result = call(monthly_kwh=600, monthly_bill_myr=300)
        self.assertEqual(result["status"], "error")
        self.assertNotIn("financial", result)


class TestBackwardCompatibility(unittest.TestCase):
    def test_v0_1_calls_without_tariff_still_work(self):
        for payload in ({"monthly_kwh": 600}, {"monthly_bill_myr": 300}):
            with self.subTest(payload):
                self.assertEqual(call(**payload)["status"], "ok")

    def test_missing_consumption_still_reports_its_own_code(self):
        result = generate_ess_proposal(BASE)
        self.assertEqual(result["code"], "MISSING_CONSUMPTION_INPUT")


if __name__ == "__main__":
    unittest.main()
