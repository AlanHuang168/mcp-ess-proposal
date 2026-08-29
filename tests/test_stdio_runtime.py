import asyncio
import sys
import unittest
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOL_NAME = "generate_ess_proposal"


async def call_stdio_server():
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
            result = await session.call_tool(
                TOOL_NAME,
                {
                    "customer_type": "residential",
                    "location": "Selangor",
                    "monthly_kwh": 500,
                },
            )
            return tools, result


class McpStdioRuntimeTests(unittest.TestCase):
    def test_stdio_runtime_lists_and_calls_core_tool(self):
        tools, result = asyncio.run(call_stdio_server())

        self.assertEqual([tool.name for tool in tools.tools], [TOOL_NAME])
        self.assertFalse(result.isError)
        self.assertEqual(result.structuredContent["status"], "ok")
        self.assertEqual(
            result.structuredContent["assumptions"]["calculation_method"],
            "deterministic-v0",
        )


if __name__ == "__main__":
    unittest.main()
