import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp import types  # noqa: E402
from mcp_ess_proposal.server import (  # noqa: E402
    GENERATE_ESS_PROPOSAL_INPUT_SCHEMA,
    GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA,
    SERVER_NAME,
    TOOL_NAME,
    create_server,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(coro):
    return asyncio.run(coro)


async def list_tools(server):
    handler = server.request_handlers[types.ListToolsRequest]
    result = await handler(types.ListToolsRequest())
    return result.root.tools


async def call_tool(server, arguments):
    await list_tools(server)
    handler = server.request_handlers[types.CallToolRequest]
    result = await handler(
        types.CallToolRequest(
            params=types.CallToolRequestParams(name=TOOL_NAME, arguments=arguments)
        )
    )
    return result.root


def text_json(call_result):
    assert len(call_result.content) == 1
    return json.loads(call_result.content[0].text)


class McpServerAdapterTests(unittest.TestCase):
    def test_server_name(self):
        server = create_server()

        self.assertEqual(server.name, SERVER_NAME)

    def test_registers_only_core_v0_tool(self):
        server = create_server()

        tools = run(list_tools(server))
        self.assertEqual([tool.name for tool in tools], [TOOL_NAME])

    def test_tool_schema_matches_public_contract_inputs(self):
        server = create_server()

        tool = run(list_tools(server))[0]
        self.assertEqual(tool.inputSchema, GENERATE_ESS_PROPOSAL_INPUT_SCHEMA)
        self.assertFalse(tool.inputSchema["additionalProperties"])
        self.assertEqual(tool.inputSchema["required"], ["customer_type", "location"])
        self.assertEqual(
            tool.inputSchema["anyOf"],
            [{"required": ["monthly_bill_myr"]}, {"required": ["monthly_kwh"]}],
        )

    def test_tool_schema_matches_public_contract_outputs(self):
        server = create_server()

        tool = run(list_tools(server))[0]
        self.assertEqual(tool.outputSchema, GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA)
        self.assertEqual(
            [branch["properties"]["status"]["const"] for branch in tool.outputSchema["oneOf"]],
            ["ok", "error"],
        )
        self.assertFalse(tool.outputSchema["oneOf"][0]["additionalProperties"])
        self.assertFalse(tool.outputSchema["oneOf"][1]["additionalProperties"])

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
        result = call_result.structuredContent

        self.assertFalse(call_result.isError)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["assumptions"]["calculation_method"], "deterministic-v0")
        self.assertIn("recommended_config", result)
        self.assertIn("financial", result)
        self.assertEqual(text_json(call_result), result)
        self.assertNotIn("proposal_id", result)
        self.assertNotIn("company_contact", result)

    def test_tool_returns_sdk_validation_error_for_missing_consumption(self):
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

        self.assertTrue(call_result.isError)
        self.assertIn("Input validation error", call_result.content[0].text)

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
