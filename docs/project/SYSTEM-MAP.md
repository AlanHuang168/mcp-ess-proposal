# System Map

Status: Initial

Date: 2026-08-29

## Runtime Boundary

```text
Host / MCP Client
  -> stdio transport
  -> mcp_ess_proposal.__main__
  -> mcp_ess_proposal.server
  -> mcp_ess_proposal.calculator
  -> mcp_ess_proposal.models
  -> mcp_ess_proposal.data
  -> bundled neutral fixtures
```

## Runtime Modules

- `src/mcp_ess_proposal/__main__.py`: package entrypoint.
- `src/mcp_ess_proposal/server.py`: MCP Server Adapter（MCP 服务适配层） and Tool（工具） registration.
- `src/mcp_ess_proposal/calculator.py`: Deterministic Calculation（确定性计算） Core.
- `src/mcp_ess_proposal/models.py`: neutral domain models.
- `src/mcp_ess_proposal/data.py`: package-resource fixture loading.
- `src/mcp_ess_proposal/fixtures/*.json`: neutral sample data.

## Dependency Boundary

- `server.py` may depend on the MCP SDK.
- `calculator.py`, `models.py`, `data.py`, and fixtures must not depend on the MCP SDK.
- Core v0 has no required environment variables and no required Secret（密钥）.
- Core v0 uses stdio only; Remote HTTP（远程 HTTP）, Authentication（鉴权）, Provider（供应商）, OCR, LLM, CRM, DB, Lead（线索）, Skill（技能）, and Prompt（提示词） behavior are outside the accepted runtime boundary.

## Tool Boundary

Included Core v0 public Tool（工具）:

- `generate_ess_proposal`

Excluded from Core v0:

- `submit_consultation_lead`
- `generate_ess_proposal_from_bill`
- `hello`

## External Source References

- Source project: `<PRIVATE_SOURCE_ROOT>`.
- Comparison project: `<PARTNER_PROJECT_ROOT>`.

These paths are source evidence only. They are not runtime dependencies of `mcp-ess-proposal`.

## Known Architecture Drift

`partner-plugin-project` is retained as Skill / Knowledge / Workflow（技能 / 知识 / 工作流） scope. Its current runtime tool registration, OCR / LLM integration, data assumptions, and deterministic calculation logic are recorded as existing Architecture Drift（既有架构漂移） and are not used as the boundary reference for this project.
