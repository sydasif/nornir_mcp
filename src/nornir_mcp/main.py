"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

from fastmcp import FastMCP

from nornir_mcp.resources import get_capabilities
from nornir_mcp.tools import (
    list_nornir_inventory,
    reload_nornir_inventory,
    run_napalm_getter,
)


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    # Register Tools
    mcp.tool(list_nornir_inventory)
    mcp.tool(run_napalm_getter)
    mcp.tool(reload_nornir_inventory)

    # Register Resources
    @mcp.resource("nornir://capabilities")
    def capabilities_resource() -> dict:
        """Supported automation getter and getter descriptions."""
        return get_capabilities()

    mcp.run()


if __name__ == "__main__":
    main()
