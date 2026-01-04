"""Nornir tools module for Model Context Protocol (MCP) server.

This module provides the core network automation tools exposed by the
MCP server. It includes functionality for device discovery and fact
gathering using the NAPALM library for standardized network device
interactions.
"""

from nornir_napalm.plugins.tasks import napalm_get

from .nornir_init import init_nornir


def list_all_hosts() -> str:
    """List all hosts in the inventory.

    Retrieves and formats information about all network devices in the
    Nornir inventory. This function provides a high-level overview of
    available network infrastructure for LLMs to understand the topology.

    Returns:
        str: Formatted string containing available hosts with name, IP,
            and platform information. Returns error message if inventory
            access fails.
    """
    try:
        nr = init_nornir()
        output = ["Available Hosts:"]

        if not nr.inventory.hosts:
            return "No hosts found in inventory."

        for host in nr.inventory.hosts.values():
            output.append(
                f"- Name: {host.name}, IP: {host.hostname}, Platform: {host.platform}"
            )
        return "\n".join(output)
    except Exception as e:
        return f"Error listing hosts: {str(e)}"


def get_device_facts(target_host: str = None) -> str:
    """Get device facts for a specific host or all hosts.

    Retrieves detailed device information using NAPALM, including model,
    serial number, OS version, vendor, uptime, and interface list. This
    function enables LLMs to access comprehensive device information for
    network automation tasks.

    The function uses NAPALM's standardized interface to gather facts from
    network devices, providing consistent data across different vendor
    platforms.

    Args:
        target_host (str, optional): Specific hostname to query. If None,
            facts for all hosts in inventory are retrieved.

    Returns:
        str: Formatted string containing device facts for the specified
            host(s). Returns error message if fact gathering fails.

    Security Considerations:
        - Device credentials are managed through Nornir inventory
        - Network connectivity and device access permissions required
        - Sensitive device information is exposed through this function
    """
    try:
        nr = init_nornir()

        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return f"No hosts found matching criteria: {target_host}"

        result = nr.run(task=napalm_get, getters=["facts"])

        return result

    except Exception as e:
        return f"Error getting facts: {str(e)}"
