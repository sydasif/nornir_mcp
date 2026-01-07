"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.

Example:
    Run the server directly::

        uv run nornir-mcp

Attributes:
    mcp: FastMCP instance that handles the Model Context Protocol communication.
"""

from fastmcp import FastMCP

from nornir_mcp.resources import get_getters, get_netmiko_commands
from nornir_mcp.tools import (
    list_nornir_inventory,
    reload_nornir_inventory,
    run_napalm_getter,
    run_netmiko_command,
)


def main():
    """Initialize and run the Nornir MCP server.

    Sets up the FastMCP server instance and registers all available tools
    and resources for network automation tasks. The server provides
    standardized interfaces for interacting with network devices via
    NAPALM getters and Netmiko commands.

    The server registers the following tools:
        - list_nornir_inventory: List configured network hosts
        - run_napalm_getter: Execute NAPALM getters on devices
        - run_netmiko_command: Execute CLI commands on devices
        - reload_nornir_inventory: Reload inventory from disk

    The server registers the following resources:
        - nornir://napalm_getters: Available NAPALM getters
        - nornir://netmiko_commands: Common Netmiko CLI commands

    Raises:
        Exception: If server initialization fails
    """
    mcp = FastMCP("nornir-mcp")

    # Register Tools
    mcp.tool(list_nornir_inventory)
    mcp.tool(run_napalm_getter)
    mcp.tool(run_netmiko_command)
    mcp.tool(reload_nornir_inventory)

    # Register Resources
    @mcp.resource("nornir://napalm_getters")
    def napalm_getters_resource() -> dict:
        """Supported NAPALM getters and descriptions."""
        return get_getters()

    @mcp.resource("nornir://netmiko_commands")
    def netmiko_commands_resource() -> dict:
        """Top 10 common Netmiko CLI commands and descriptions."""
        return get_netmiko_commands()

    mcp.run()


if __name__ == "__main__":
    main()
