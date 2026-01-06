"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

from fastmcp import FastMCP

from nornir_mcp.resources import get_capabilities, get_inventory
from nornir_mcp.tools import (
    list_all_hosts,
    reload_nornir_inventory,
    run_getter,
)


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    # Register Tools
    mcp.tool(list_all_hosts)
    mcp.tool(reload_nornir_inventory)
    mcp.tool(run_getter)

    # Register Resources
    @mcp.resource("nornir://inventory")
    def inventory_resource() -> dict:
        """The current Nornir inventory (hosts, IPs, platforms)."""
        return get_inventory()

    @mcp.resource("nornir://capabilities")
    def capabilities_resource() -> dict:
        """Supported automation capabilities and getter descriptions."""
        return get_capabilities()

    mcp.run()


if __name__ == "__main__":
    main()
