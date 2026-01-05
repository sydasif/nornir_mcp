from fastmcp import FastMCP

from nornir_mcp.resources import napalm_getters
from nornir_mcp.tools import get_device_data, list_all_hosts


def main():
    mcp = FastMCP("nornir-mcp")

    # Register tools
    mcp.tool(list_all_hosts)
    mcp.tool(get_device_data)

    # Register resources
    mcp.resource("nornir://napalm-getters")(napalm_getters)

    mcp.run()


if __name__ == "__main__":
    main()
