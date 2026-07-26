"""MCP server exposing AgentShield's mock business tools.

Business logic for every tool lives in a plain `..._impl` function; the
`@mcp.tool()`-decorated function is a thin wrapper. This keeps tool logic
unit-testable without depending on MCP transport internals, and is the
pattern every tool added in M1 (get_customer, get_order, track_shipment,
update_shipping_address, request_refund, issue_discount,
escalate_to_human) will follow.

This service is reachable only on the internal Docker network — see
docker-compose.yml, where it deliberately has no published host port.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("AgentShield Tools")


def ping_impl() -> dict:
    """Business logic for the health-check tool."""
    return {"status": "ok"}


@mcp.tool()
def ping() -> dict:
    """Health-check tool that confirms the MCP transport is wired correctly."""
    return ping_impl()


app = mcp.streamable_http_app()
