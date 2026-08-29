"""End-to-end MCP host round trip for Core v0.2.

Drives a real stdio MCP client session the same way an MCP Host does:
initialize, discover the tool, then call it on the success path, the new
user-supplied tariff path, and the new inconsistency error path.
"""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL_NAME = "generate_ess_proposal"


async def _round_trip(calls: list[dict]) -> tuple[object, list]:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_ess_proposal"],
        env={"PYTHONPATH": str(PROJECT_ROOT / "src")},
        cwd=PROJECT_ROOT,
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            results = [await session.call_tool(TOOL_NAME, args) for args in calls]
            return tools, results


class McpHostRoundTripV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools, cls.results = asyncio.run(
            _round_trip(
                [
                    {"customer_type": "residential", "location": "Selangor", "monthly_kwh": 600},
                    {
                        "customer_type": "residential",
                        "location": "Selangor",
                        "monthly_kwh": 600,
                        "tariff_myr_per_kwh": 0.60,
                    },
                    {
                        "customer_type": "residential",
                        "location": "Selangor",
                        "monthly_kwh": 600,
                        "monthly_bill_myr": 300,
                    },
                ]
            )
        )

    def test_discovery_still_exposes_exactly_one_tool(self):
        self.assertEqual([tool.name for tool in self.tools.tools], [TOOL_NAME])

    def test_discovered_input_schema_declares_tariff(self):
        schema = self.tools.tools[0].inputSchema
        self.assertIn("tariff_myr_per_kwh", schema["properties"])
        self.assertEqual(schema["properties"]["tariff_myr_per_kwh"]["maximum"], 10)
        self.assertEqual(schema["additionalProperties"], False)

    def test_discovered_output_schema_declares_v0_2_fields(self):
        ok_schema = self.tools.tools[0].outputSchema["oneOf"][0]
        self.assertIn("tariff_source", ok_schema["required"])
        self.assertIn("consumption_source", ok_schema["required"])
        self.assertIn(
            "investment_scope", ok_schema["properties"]["financial"]["required"]
        )

    def test_discovered_error_schema_declares_new_code(self):
        error_schema = self.tools.tools[0].outputSchema["oneOf"][1]
        self.assertIn(
            "INCONSISTENT_CONSUMPTION_INPUT", error_schema["properties"]["code"]["enum"]
        )

    def test_default_tariff_path_over_the_wire(self):
        content = self.results[0].structuredContent
        self.assertEqual(content["status"], "ok")
        self.assertEqual(content["tariff_source"], "default_residential_tiered")
        self.assertEqual(content["consumption_source"], "monthly_kwh")
        self.assertEqual(content["financial"]["investment_scope"], "pv_only")

    def test_user_tariff_path_over_the_wire(self):
        content = self.results[1].structuredContent
        self.assertEqual(content["tariff_source"], "user_provided")
        self.assertEqual(content["estimated_avg_tariff_myr_per_kwh"], 0.60)
        self.assertNotEqual(
            content["financial"]["estimated_annual_savings_myr"],
            self.results[0].structuredContent["financial"]["estimated_annual_savings_myr"],
        )

    def test_inconsistent_input_reaches_the_host_as_a_structured_error(self):
        content = self.results[2].structuredContent
        self.assertEqual(content["status"], "error")
        self.assertEqual(content["code"], "INCONSISTENT_CONSUMPTION_INPUT")
        self.assertIn("implied_bill_myr", content["details"])

    def test_no_secret_or_internal_path_leaks_over_the_wire(self):
        for result in self.results:
            payload = str(result.structuredContent)
            self.assertNotIn("/Users/", payload)
            self.assertNotIn("Traceback", payload)


if __name__ == "__main__":
    unittest.main()
