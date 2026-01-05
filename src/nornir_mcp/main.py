from fastmcp import FastMCP

from .nornir_tools import (
    get_device_data,
    list_all_hosts,
    napalm_getters,
)

mcp = FastMCP("nornir-mcp")

# Resources
mcp.resource("napalm_getters")(napalm_getters)

# Tools
mcp.tool()(list_all_hosts)
mcp.tool()(get_device_data)


def main():
    """Main entry point for the Nornir Model Context Protocol (MCP) server.

    Initializes and runs the FastMCP server with Nornir network automation tools.
    The server exposes network device management capabilities to LLMs through
    standardized tools for device discovery, fact gathering, and configuration
    management.

    The server provides the following tools:
    - list_all_hosts: Lists all network devices in the Nornir inventory
    - get_device_data: Retrieves detailed device information using NAPALM

    The server also provides the following resource:
    - napalm_getters: Lists supported NAPALM getters

    Returns:
        None: This function runs the MCP server which blocks indefinitely.
    """
    mcp.run()


if __name__ == "__main__":
    main()
