"""Main entry point for Nornir MCP server.

This module serves as the main entry point for the Nornir MCP server.
The actual implementation is split between:
- nornir_init.py: Handles Nornir initialization and instance management
- nornir_tools.py: Contains the tool definitions
"""

from fastmcp import FastMCP

from .nornir_tools import get_device_facts, list_all_hosts

# Initialize the FastMCP server
mcp = FastMCP("nornir-mcp")

# Register tools
mcp.tool()(list_all_hosts)
mcp.tool()(get_device_facts)


def main():
    """Start the Nornir MCP server.

    This function runs the FastMCP server which exposes Nornir network automation
    tools to LLMs through the Model Context Protocol. The server will continue
    running until terminated by the user.
    """
    mcp.run()


if __name__ == "__main__":
    main()
