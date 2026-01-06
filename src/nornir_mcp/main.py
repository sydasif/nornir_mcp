"""Main entry point for the Nornir Model Context Protocol (MCP) server.

This module initializes and runs the MCP server, registering all available
tools for network automation tasks.
"""

from fastmcp import FastMCP

from nornir_mcp.tools import (
    get_arp_table,
    get_facts,
    get_interfaces,
    get_interfaces_ip,
    get_mac_address_table,
    list_all_hosts,
    reload_nornir_inventory,
)


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    mcp.tool(list_all_hosts)
    mcp.tool(reload_nornir_inventory)

    mcp.tool(get_facts)
    mcp.tool(get_interfaces)
    mcp.tool(get_interfaces_ip)
    mcp.tool(get_arp_table)
    mcp.tool(get_mac_address_table)

    mcp.run()


if __name__ == "__main__":
    main()
