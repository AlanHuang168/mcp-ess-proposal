# CONTRACT AMENDMENT-0002: MCP 2.x Output Schema Normalization

Status: Accepted for Core v0.2

Date: 2026-08-29

Accepted: 2026-08-29

Human Decision（人工决策）, 2026-08-29:

- MCP SDK 2.1.1 low-level `tools/list` requires `Tool.output_schema` to declare root `type: "object"` for the negotiated stdio protocol surface.
- The Accepted Contract output schema remains semantically unchanged: top-level `oneOf` with the success object branch and error object branch.
- Runtime Discovery Schema（运行时发现 Schema） may add only the top-level `type: "object"` required by MCP 2.x.
- No success branch, error branch, business field, `required`, `enum`, or `additionalProperties` constraint may change under this amendment.
- This authorization is not generalized to any other schema rewrite.

Amends: `docs/contracts/mcp-tools.md` (Accepted MCP Tool Contract, Core v0.2)

Governing ADR: `docs/adr/ADR-0001-mcp-ess-open-source-boundaries.md` (Accepted, unchanged by this amendment)

## Normalization Rule

Accepted Contract representation:

```yaml
oneOf:
  - success object
  - error object
```

MCP 2.x Runtime Discovery representation:

```yaml
type: object
oneOf:
  - success object
  - error object
```

This is a Protocol-Required Normalization（协议要求的规范化） only. It is deterministic, minimal, documented, tested, and does not change the accepted value set or business field semantics.

## Contract Fidelity Rule

Contract Fidelity（契约保真） is evaluated in two layers:

- Semantic Contract Fidelity（业务契约语义保真）: business fields, branches, accepted values, required fields, enum values, and `additionalProperties` constraints must remain equivalent to the Accepted Contract.
- Protocol Representation Fidelity（协议表示保真）: the adapter may apply an explicitly approved protocol-required normalization.

For Core v0.2, the only approved normalization is adding top-level `type: "object"` to the MCP 2.x Runtime Discovery output schema.

## Validation Requirements

- Accepted Contract branches unchanged.
- Runtime discovery schema contains root `type: "object"`.
- Success payload validation passes.
- Error payload validation passes.
- Illegal payloads remain invalid.
- `additionalProperties: false` remains on both output branches.
- MCP 2.1.1 `tools/list` passes.
- MCP 2.1.1 `tools/call` passes.
- Full tests pass.
- Schema semantic-equivalence validation passes.
