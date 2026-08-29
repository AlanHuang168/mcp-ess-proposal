import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import jsonschema  # noqa: E402
from mcp import types  # noqa: E402
from mcp_ess_proposal.server import (  # noqa: E402
    CALL_TOOL_METHOD,
    GENERATE_ESS_PROPOSAL_CONTRACT_OUTPUT_SCHEMA,
    GENERATE_ESS_PROPOSAL_INPUT_SCHEMA,
    GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA,
    LIST_TOOLS_METHOD,
    SERVER_NAME,
    TOOL_NAME,
    create_server,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(coro):
    return asyncio.run(coro)


async def list_tools(server):
    request = types.ListToolsRequest()
    entry = server.get_request_handler(request.method)
    result = await entry.handler(None, request.params or types.PaginatedRequestParams())
    return result.tools


async def call_tool(server, arguments):
    await list_tools(server)
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(name=TOOL_NAME, arguments=arguments)
    )
    entry = server.get_request_handler(request.method)
    return await entry.handler(None, request.params)


def text_json(call_result):
    assert len(call_result.content) == 1
    return json.loads(call_result.content[0].text)


class McpServerAdapterTests(unittest.TestCase):
    def test_server_name(self):
        server = create_server()

        self.assertEqual(server.name, SERVER_NAME)

    def test_registers_only_core_v0_tool(self):
        server = create_server()

        self.assertIsNotNone(server.get_request_handler(LIST_TOOLS_METHOD))
        self.assertIsNotNone(server.get_request_handler(CALL_TOOL_METHOD))
        tools = run(list_tools(server))
        self.assertEqual([tool.name for tool in tools], [TOOL_NAME])

    def test_tool_schema_matches_public_contract_inputs(self):
        server = create_server()

        tool = run(list_tools(server))[0]
        self.assertEqual(tool.input_schema, GENERATE_ESS_PROPOSAL_INPUT_SCHEMA)
        self.assertFalse(tool.input_schema["additionalProperties"])
        self.assertEqual(tool.input_schema["required"], ["customer_type", "location"])
        self.assertEqual(
            tool.input_schema["anyOf"],
            [{"required": ["monthly_bill_myr"]}, {"required": ["monthly_kwh"]}],
        )

    def test_tool_schema_matches_public_contract_outputs(self):
        server = create_server()

        tool = run(list_tools(server))[0]
        self.assertEqual(tool.output_schema, GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA)
        self.assertEqual(tool.output_schema["type"], "object")
        self.assertEqual(
            [
                branch["properties"]["status"]["const"]
                for branch in tool.output_schema["oneOf"]
            ],
            ["ok", "error"],
        )
        self.assertFalse(tool.output_schema["oneOf"][0]["additionalProperties"])
        self.assertFalse(tool.output_schema["oneOf"][1]["additionalProperties"])

    def test_output_schema_normalization_preserves_accepted_contract_branches(self):
        runtime_schema = GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA.copy()

        self.assertEqual(runtime_schema.pop("type"), "object")
        self.assertEqual(runtime_schema, GENERATE_ESS_PROPOSAL_CONTRACT_OUTPUT_SCHEMA)
        self.assertEqual(
            GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA["oneOf"],
            GENERATE_ESS_PROPOSAL_CONTRACT_OUTPUT_SCHEMA["oneOf"],
        )
        for branch in GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA["oneOf"]:
            self.assertFalse(branch["additionalProperties"])

    def test_tool_calls_core_and_returns_contract_shaped_success(self):
        server = create_server()

        call_result = run(
            call_tool(
                server,
                {
                    "customer_type": "residential",
                    "location": "Selangor",
                    "monthly_kwh": 500,
                },
            )
        )
        result = call_result.structured_content

        self.assertFalse(call_result.is_error)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["assumptions"]["calculation_method"], "deterministic-v0")
        self.assertIn("recommended_config", result)
        self.assertIn("financial", result)
        self.assertEqual(text_json(call_result), result)
        self.assertNotIn("proposal_id", result)
        self.assertNotIn("company_contact", result)
        jsonschema.validate(result, GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA)

    def test_tool_returns_contract_error_for_missing_consumption(self):
        server = create_server()

        call_result = run(
            call_tool(
                server,
                {
                    "customer_type": "residential",
                    "location": "Selangor",
                },
            )
        )

        self.assertTrue(call_result.is_error)
        self.assertEqual(call_result.structured_content["status"], "error")
        self.assertEqual(
            call_result.structured_content["code"],
            "MISSING_CONSUMPTION_INPUT",
        )
        self.assertEqual(text_json(call_result), call_result.structured_content)
        jsonschema.validate(
            call_result.structured_content,
            GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA,
        )

    def test_output_schema_still_rejects_illegal_payloads(self):
        invalid_success = {
            "status": "ok",
            "summary": "x",
            "customer_type": "residential",
            "location": "Selangor",
            "estimated_monthly_kwh": 500,
            "estimated_avg_tariff_myr_per_kwh": 0.4,
            "tariff_source": "user_provided",
            "consumption_source": "monthly_kwh",
            "recommended_config": {
                "pv_kwp": 4.0,
                "storage_recommended": False,
                "storage_kw": 0,
                "storage_kwh": 0,
                "notes": [],
            },
            "financial": {
                "estimated_investment_myr": 12000,
                "investment_scope": "pv_only",
                "estimated_annual_generation_kwh": 6000,
                "estimated_annual_savings_myr": 2400,
                "estimated_payback_years": 5,
            },
            "assumptions": {"currency": "MYR", "calculation_method": "deterministic-v0"},
            "risks": [],
            "data_confidence_notes": [],
            "disclaimer": "x",
            "unexpected": "still forbidden",
        }

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_success, GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA)

    def test_output_schema_rejects_invalid_enum_values(self):
        invalid_error = {
            "status": "error",
            "code": "NEW_UNAPPROVED_CODE",
            "message": "x",
        }

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_error, GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA)

    def test_excluded_tools_are_not_registered(self):
        server = create_server()

        tools = {tool.name for tool in run(list_tools(server))}
        self.assertNotIn("hello", tools)
        self.assertNotIn("submit_consultation_lead", tools)
        self.assertNotIn("generate_ess_proposal_from_bill", tools)

    def test_core_modules_do_not_import_mcp_sdk(self):
        core_files = ["calculator.py", "models.py", "data.py"]

        for core_file in core_files:
            text = (PROJECT_ROOT / "src" / "mcp_ess_proposal" / core_file).read_text()
            self.assertNotIn("from mcp", text)
            self.assertNotIn("import mcp", text)


if __name__ == "__main__":
    unittest.main()
