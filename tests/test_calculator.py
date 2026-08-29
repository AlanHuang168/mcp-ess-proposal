import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp_ess_proposal.calculator import (  # noqa: E402
    estimate_residential_avg_tariff,
    generate_ess_proposal,
)
from mcp_ess_proposal.data import DEFAULT_CALCULATION_DATA  # noqa: E402
from mcp_ess_proposal.data import load_default_calculation_data, load_sample_products  # noqa: E402


class GenerateEssProposalTests(unittest.TestCase):
    def test_generates_from_monthly_bill(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
                "monthly_bill_myr": 450,
            }
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["customer_type"], "residential")
        self.assertGreater(result["estimated_monthly_kwh"], 0)
        self.assertGreater(result["recommended_config"]["pv_kwp"], 0)
        self.assertEqual(result["assumptions"]["calculation_method"], "deterministic-v0")

    def test_success_output_uses_core_contract_shape(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
                "monthly_kwh": 500,
            }
        )

        self.assertEqual(
            set(result),
            {
                "status",
                "summary",
                "customer_type",
                "location",
                "monthly_bill_myr",
                "estimated_monthly_kwh",
                "estimated_avg_tariff_myr_per_kwh",
                "tariff_source",
                "consumption_source",
                "recommended_config",
                "financial",
                "assumptions",
                "risks",
                "data_confidence_notes",
                "disclaimer",
            },
        )
        self.assertNotIn("proposal_id", result)
        self.assertNotIn("company_contact", result)
        self.assertNotIn("summary_text", result)

    def test_generates_from_monthly_kwh(self):
        result = generate_ess_proposal(
            {
                "customer_type": "commercial",
                "location": "Johor",
                "monthly_kwh": 1200,
            }
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["estimated_monthly_kwh"], 1200)
        self.assertEqual(result["estimated_avg_tariff_myr_per_kwh"], 0.5)

    def test_residential_tiered_tariff(self):
        avg = estimate_residential_avg_tariff(900, DEFAULT_CALCULATION_DATA)

        expected = (
            (200 * 0.218)
            + (100 * 0.334)
            + (300 * 0.516)
            + (300 * 0.546)
        ) / 900
        self.assertAlmostEqual(avg, expected, places=6)

    def test_budget_caps_pv_size(self):
        result = generate_ess_proposal(
            {
                "customer_type": "commercial",
                "location": "Kuala Lumpur",
                "monthly_kwh": 5000,
                "budget_myr": 18000,
            }
        )

        self.assertEqual(result["status"], "ok")
        self.assertLessEqual(result["recommended_config"]["pv_kwp"], 4)

    def test_backup_request_adds_storage(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Penang",
                "monthly_kwh": 600,
                "need_backup": True,
            }
        )

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["recommended_config"]["storage_recommended"])
        self.assertGreater(result["recommended_config"]["storage_kwh"], 0)

    def test_special_requirement_storage_keyword_adds_storage(self):
        result = generate_ess_proposal(
            {
                "customer_type": "factory",
                "location": "Johor",
                "monthly_kwh": 5000,
                "special_requirements": "backup power required",
            }
        )

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["recommended_config"]["storage_recommended"])

    def test_missing_consumption_input_returns_contract_error(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
            }
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "MISSING_CONSUMPTION_INPUT")

    def test_rejects_unsupported_extra_fields(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
                "monthly_kwh": 500,
                "bill_images": ["bill.jpg"],
            }
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "VALIDATION_ERROR")

    def test_rejects_boolean_as_numeric_input(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
                "monthly_kwh": True,
            }
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "VALIDATION_ERROR")

    def test_rejects_non_boolean_need_backup(self):
        result = generate_ess_proposal(
            {
                "customer_type": "residential",
                "location": "Selangor",
                "monthly_kwh": 500,
                "need_backup": "yes",
            }
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["code"], "VALIDATION_ERROR")

    def test_default_calculation_fixture_loads(self):
        data = load_default_calculation_data()

        self.assertEqual(data.annual_yield_per_kwp, 1350)
        self.assertEqual(data.coverage_ratio, 0.7)
        self.assertEqual(len(data.residential_tiers), 5)

    def test_sample_product_fixture_loads(self):
        products = load_sample_products()

        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]["data_confidence"], "sample")


if __name__ == "__main__":
    unittest.main()
