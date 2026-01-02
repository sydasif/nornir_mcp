"""MCP server for Nornir network automation.

This module exposes Nornir network automation capabilities through the Model Context Protocol (MCP),
allowing LLMs to interact with network devices via standardized tools. The server provides
functionality to list network hosts and retrieve device facts using NAPALM.

The server uses lazy initialization for the Nornir instance to optimize resource usage
and maintains a single connection context across all tool invocations.
"""

from mcp.server.fastmcp import FastMCP
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get

# Initialize the FastMCP server instance
# The name "nornir-mcp" is what the LLM will see
mcp = FastMCP("nornir-mcp")

# Global Nornir instance (loaded lazily)
nr = None


def get_nornir():
    """Initialize or return the existing Nornir instance.

    Implements lazy initialization pattern to create the Nornir instance
    only when first accessed. Subsequent calls return the same instance
    to maintain connection state and optimize resource usage.

    Returns:
        nornir.core.Nornir: Initialized Nornir instance configured with config.yaml
    """
    global nr
    if nr is None:
        nr = InitNornir(config_file="config.yaml")
    return nr


@mcp.tool()
def list_hosts() -> str:
    """List all hosts defined in the Nornir inventory.

    Retrieves the complete list of network devices from the Nornir inventory
    and formats them as a human-readable string. Each host includes its
    name, IP address, and platform information.

    This tool provides LLMs with visibility into the available network
    infrastructure for planning and execution purposes.

    Returns:
        str: Formatted string containing available hosts with their details.
             Format: "Available Hosts:\n- Name: <name>, IP: <ip>, Platform: <platform>"
             Returns error message if inventory access fails.
    """
    try:
        nr = get_nornir()
        output = []
        output.append("Available Hosts:")
        for host in nr.inventory.hosts.values():
            output.append(
                f"- Name: {host.name}, IP: {host.hostname}, Platform: {host.platform}"
            )
        return "\n".join(output)
    except Exception as e:
        return f"Error listing hosts: {e}"


@mcp.tool()
def get_network_facts(target_host: str = None) -> str:
    """Gather device facts (model, serial, OS version) using NAPALM.

    Retrieves comprehensive device information from network equipment using
    the NAPALM library. Can target a specific device or retrieve facts from
    all available devices in the inventory.

    This tool enables LLMs to understand device capabilities, versions, and
    hardware characteristics for informed decision-making during network
    automation tasks.

    Args:
        target_host (str, optional): Specific hostname to query (e.g., 'router').
                                   If None, retrieves facts from all hosts.
                                   Defaults to None.

    Returns:
        str: Formatted string containing device facts for each queried host.
             Format includes model, serial number, OS version, and vendor.
             Returns error message if fact gathering fails for any device.

    Security Considerations:
        - Device credentials are managed through Nornir inventory configuration
        - Network connectivity requirements must be satisfied for fact gathering
        - Device access permissions must be properly configured
    """
    try:
        nr = get_nornir()

        # Filter inventory if a specific host is requested
        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return f"No hosts found for filter: {target_host}"

        # Run the NAPALM task
        result = nr.run(task=napalm_get, getters=["facts"])

        # Format the results for the LLM
        summary = []
        for host, task_result in result.items():
            if task_result.failed:
                summary.append(f"Host: {host} - FAILED to get facts")
            else:
                facts = task_result.result["facts"]
                summary.append(
                    f"Host: {host}\n"
                    f"  - Model: {facts['model']}\n"
                    f"  - Serial: {facts['serial_number']}\n"
                    f"  - OS Version: {facts['os_version']}\n"
                    f"  - Vendor: {facts['vendor']}"
                )

        return "\n".join(summary)

    except Exception as e:
        return f"Error getting facts: {e}"


if __name__ == "__main__":
    mcp.run()
