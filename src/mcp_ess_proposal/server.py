from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp import types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from . import __version__
from .calculator import generate_ess_proposal as generate_ess_proposal_core

SERVER_NAME = "mcp-ess-proposal"
TOOL_NAME = "generate_ess_proposal"
LIST_TOOLS_METHOD = types.ListToolsRequest.model_fields["method"].default
CALL_TOOL_METHOD = types.CallToolRequest.model_fields["method"].default

GENERATE_ESS_PROPOSAL_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["customer_type", "location"],
    "properties": {
        "customer_type": {
            "type": "string",
            "enum": ["residential", "commercial", "factory", "datacenter"],
            "description": "Customer segment used to select calculation assumptions.",
        },
        "location": {
            "type": "string",
            "minLength": 1,
            "maxLength": 120,
            "description": (
                "Customer location label. Core v0 treats it as metadata unless "
                "tariff data supports location-specific logic."
            ),
        },
        "monthly_bill_myr": {
            "type": "number",
            "exclusiveMinimum": 0,
            "description": (
                "Monthly electricity bill amount in MYR. At least one of "
                "monthly_bill_myr or monthly_kwh is required."
            ),
        },
        "monthly_kwh": {
            "type": "number",
            "exclusiveMinimum": 0,
            "description": (
                "Monthly electricity consumption in kWh. At least one of "
                "monthly_bill_myr or monthly_kwh is required."
            ),
        },
        "need_backup": {
            "type": "boolean",
            "default": False,
            "description": "Whether backup power is requested.",
        },
        "tariff_myr_per_kwh": {
            "type": "number",
            "exclusiveMinimum": 0,
            "maximum": 10,
            "description": (
                "Optional user-supplied average electricity tariff in MYR per kWh. "
                "When provided it is used for this calculation and overrides bundled "
                "default tariff data. Ownership of the tariff dataset and default "
                "tariff remains with the server fixtures."
            ),
        },
        "budget_myr": {
            "type": "number",
            "exclusiveMinimum": 0,
            "description": "Optional budget cap in MYR.",
        },
        "special_requirements": {
            "type": "string",
            "maxLength": 2000,
            "description": (
                "Optional free-form requirements. Core v0 may only use deterministic "
                "keyword checks documented in implementation."
            ),
        },
    },
    "anyOf": [
        {"required": ["monthly_bill_myr"]},
        {"required": ["monthly_kwh"]},
    ],
}

GENERATE_ESS_PROPOSAL_CONTRACT_OUTPUT_SCHEMA: dict[str, Any] = {
    "oneOf": [
        {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "status",
                "summary",
                "customer_type",
                "location",
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
            ],
            "properties": {
                "status": {"const": "ok"},
                "summary": {"type": "string"},
                "customer_type": {"type": "string"},
                "location": {"type": "string"},
                "monthly_bill_myr": {"type": ["number", "null"]},
                "estimated_monthly_kwh": {"type": "number"},
                "estimated_avg_tariff_myr_per_kwh": {"type": "number"},
                "tariff_source": {
                    "type": "string",
                    "enum": ["user_provided", "default_residential_tiered", "default_non_residential"],
                },
                "consumption_source": {
                    "type": "string",
                    "enum": ["monthly_kwh", "derived_from_bill"],
                },
                "recommended_config": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["pv_kwp", "storage_recommended", "storage_kw", "storage_kwh", "notes"],
                    "properties": {
                        "pv_kwp": {"type": "number"},
                        "storage_recommended": {"type": "boolean"},
                        "storage_kw": {"type": "number"},
                        "storage_kwh": {"type": "number"},
                        "notes": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "financial": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "estimated_investment_myr",
                        "investment_scope",
                        "estimated_annual_generation_kwh",
                        "estimated_annual_savings_myr",
                        "estimated_payback_years",
                    ],
                    "properties": {
                        "estimated_investment_myr": {"type": "number"},
                        "investment_scope": {"type": "string", "enum": ["pv_only"]},
                        "estimated_annual_generation_kwh": {"type": "number"},
                        "estimated_annual_savings_myr": {"type": "number"},
                        "estimated_payback_years": {"type": ["number", "null"]},
                    },
                },
                "assumptions": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["currency", "calculation_method"],
                    "properties": {
                        "currency": {"const": "MYR"},
                        "calculation_method": {"const": "deterministic-v0"},
                        "annual_yield_per_kwp": {"type": "number"},
                        "coverage_ratio": {"type": "number"},
                    },
                },
                "risks": {"type": "array", "items": {"type": "string"}},
                "data_confidence_notes": {"type": "array", "items": {"type": "string"}},
                "disclaimer": {"type": "string"},
            },
        },
        {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "code", "message"],
            "properties": {
                "status": {"const": "error"},
                "code": {
                    "type": "string",
                    "enum": [
                        "VALIDATION_ERROR",
                        "UNSUPPORTED_CUSTOMER_TYPE",
                        "MISSING_CONSUMPTION_INPUT",
                        "INCONSISTENT_CONSUMPTION_INPUT",
                        "DATA_LOAD_ERROR",
                        "INTERNAL_ERROR",
                    ],
                },
                "message": {"type": "string"},
                "details": {"type": "object", "additionalProperties": True},
            },
        },
    ],
}

GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    **GENERATE_ESS_PROPOSAL_CONTRACT_OUTPUT_SCHEMA,
}


def create_server() -> Server:
    server = Server(SERVER_NAME, version=__version__)

    async def list_tools(
        _ctx: Any,
        _params: types.PaginatedRequestParams,
    ) -> types.ListToolsResult:
        return types.ListToolsResult(
            tools=[
                types.Tool(
                    name=TOOL_NAME,
                    description=(
                        "Generate a preliminary solar and energy-storage proposal from "
                        "structured customer and consumption inputs using deterministic calculation."
                    ),
                    input_schema=GENERATE_ESS_PROPOSAL_INPUT_SCHEMA,
                    output_schema=GENERATE_ESS_PROPOSAL_OUTPUT_SCHEMA,
                )
            ]
        )

    async def call_tool(
        _ctx: Any,
        params: types.CallToolRequestParams,
    ) -> types.CallToolResult:
        arguments = params.arguments or {}
        if params.name != TOOL_NAME:
            result = {
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "Unknown tool.",
                "details": {"tool": params.name},
            }
        else:
            result = generate_ess_proposal_core(arguments)

        return types.CallToolResult(
            content=[
                types.TextContent(
                    text=json.dumps(
                        result,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
            ],
            structured_content=result,
            is_error=result.get("status") == "error",
        )

    server.add_request_handler(LIST_TOOLS_METHOD, types.PaginatedRequestParams, list_tools)
    server.add_request_handler(CALL_TOOL_METHOD, types.CallToolRequestParams, call_tool)

    return server


async def run_stdio() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )


def main() -> None:
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
