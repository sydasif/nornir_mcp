"""Main entry point for Nornir Model Context Protocol (MCP) server.

This module initializes the FastMCP server and registers the available
Nornir tools for network automation tasks. The server exposes network
device management capabilities to LLMs through standardized MCP tools.
"""

from fastmcp import FastMCP

from .nornir_tools import get_device_facts, list_all_hosts

mcp = FastMCP("nornir-mcp")

# Register tools
mcp.tool()(list_all_hosts)
mcp.tool()(get_device_facts)


def main():
    """Run the Nornir MCP server.

    Starts the Model Context Protocol server which exposes Nornir
    network automation tools to LLMs. The server will continue
    running until terminated by the user.
    """
    mcp.run()


if __name__ == "__main__":
    main()
