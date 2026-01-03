"""Main entry point for Nornir Model Context Protocol (MCP) server."""

from fastmcp import FastMCP

from .nornir_tools import get_device_facts, list_all_hosts

mcp = FastMCP("nornir-mcp")

# Register tools
mcp.tool()(list_all_hosts)
mcp.tool()(get_device_facts)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
