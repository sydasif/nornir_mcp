"""Main entry point for Nornir Model Context Protocol (MCP) server.

This module initializes the FastMCP server and registers the available
Nornir tools for network automation tasks. The server exposes network
device management capabilities to LLMs through standardized MCP tools.

The server exposes these primary tools:
1. `list_all_hosts()`: Lists all network devices in the Nornir inventory
   with names, IP addresses, and platforms
2. `get_device_facts(target_host: str = None)`: Retrieves detailed device
   information (model, serial, OS version, vendor, etc.) using NAPALM
3. `get_device_health(target_host: str = None)`: Analyzes device health
   (CPU, Memory, Errors) and returns a scored report with 0-100 health score
"""

from fastmcp import FastMCP
from .nornir_tools import get_device_facts, list_all_hosts, get_device_health  # Update import

mcp = FastMCP("nornir-mcp")

# Register tools
mcp.tool()(list_all_hosts)
mcp.tool()(get_device_facts)
mcp.tool()(get_device_health)  # Register tool


def main():
    """Run the Nornir MCP server.

    Starts the Model Context Protocol server which exposes Nornir
    network automation tools to LLMs. The server will continue
    running until terminated by the user.
    """
    mcp.run()


if __name__ == "__main__":
    main()
