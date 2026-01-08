"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

from fastmcp import FastMCP

from nornir_mcp.resources import get_getters, get_netmiko_commands
from nornir_mcp.tools import (
    download_directory,
    download_file,
    list_nornir_inventory,
    reload_nornir_inventory,
    run_napalm_getter,
    run_netmiko_command,
    run_paramiko_command,
    upload_directory,
    upload_file,
)


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    # Register Tools
    mcp.tool(list_nornir_inventory)
    mcp.tool(reload_nornir_inventory)

    # Device Interaction
    mcp.tool(run_napalm_getter)
    mcp.tool(run_netmiko_command)

    # Linux/Paramiko Interaction
    mcp.tool(run_paramiko_command)
    mcp.tool(upload_file)
    mcp.tool(upload_directory)
    mcp.tool(download_file)
    mcp.tool(download_directory)

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
