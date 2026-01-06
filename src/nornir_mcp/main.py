"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

import json
import os

from fastmcp import FastMCP

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
    def supported_getters() -> dict[str, dict[str, str]]:
        """Return the list of supported NAPALM getters.

        This resource provides a list of valid getter names that can be used with
        the `run_getter` tool.

        Returns:
            dict: A dictionary containing the list of supported getters and their descriptions.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, "supported_getters.json")

            with open(json_path) as f:
                data = json.load(f)
            return data
        except Exception:
            return {"supported_getters": {}}

    mcp.run()


if __name__ == "__main__":
    main()
