from fastmcp import FastMCP

from nornir_mcp.constants import ALLOWED_GETTERS
from nornir_mcp.tools import get_device_data, list_all_hosts


def main():
    """Initialize and run the Nornir MCP server."""
    mcp = FastMCP("nornir-mcp")

    # Register tools
    mcp.tool(list_all_hosts)
    mcp.tool(get_device_data)

    # Register resource using decorator pattern
    @mcp.resource("nornir://napalm-getters")
    def napalm_getters():
        """Return the list of allowed NAPALM getters.

        This resource provides a list of valid getter names that can be used with
        the `get_device_data` tool, along with their descriptions.

        Returns:
            dict: A dictionary mapping getter names to their descriptions.
        """
        return {"napalm_getters": ALLOWED_GETTERS}

    mcp.run()


if __name__ == "__main__":
    main()
