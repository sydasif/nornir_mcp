"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

from fastmcp import FastMCP

from nornir_mcp.runners.napalm_runner import NapalmRunner
from nornir_mcp.tools import (
    list_all_hosts,
    reload_nornir_inventory,
    run_getter,
)


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    mcp.tool(list_all_hosts)
    mcp.tool(reload_nornir_inventory)
    mcp.tool(run_getter)

    @mcp.resource("nornir://supported-getters")
    def supported_getters() -> dict[str, list[str]]:
        """Return the list of supported NAPALM getters.

        This resource provides a list of valid getter names that can be used with
        the `run_getter` tool.

        Returns:
            dict: A dictionary containing the list of supported getters.
        """
        return {"supported_getters": sorted(list(NapalmRunner.SUPPORTED_GETTERS))}

    mcp.run()


if __name__ == "__main__":
    main()
