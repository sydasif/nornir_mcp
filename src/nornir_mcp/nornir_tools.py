"""Nornir tools module for Model Context Protocol (MCP) server.

This module provides the core network automation tools that are exposed
through the MCP server. It includes functions for device discovery,
fact gathering, and configuration management using the Nornir framework
and NAPALM library.

The tools enable LLMs to interact with network devices through standardized
interfaces for network automation tasks.
"""

from nornir_napalm.plugins.tasks import napalm_get

from .mcp_app import mcp
from .nornir_init import init_nornir

# Supported NAPALM getters with descriptions
# These are the data getters that can be used with the get_device_data function
ALLOWED_GETTERS = {
    "facts": "Basic device information",
    "interfaces": "Interface state and speed",
    "interfaces_ip": "IP addressing per interface",
    "bgp_neighbors": "BGP neighbor summary",
    "lldp_neighbors": "LLDP neighbor discovery",
    "arp_table": "ARP entries",
    "mac_address_table": "MAC address table",
    "environment": "Power, fans, temperature",
}


@mcp.resource
def napalm_getters():
    return {"napalm_getters": ALLOWED_GETTERS}


@mcp.tool
def list_all_hosts():
    try:
        nr = init_nornir()

        if not nr.inventory.hosts:
            return {"hosts": {}}

        hosts = {
            host.name: {
                "name": host.name,
                "ip": host.hostname,
                "platform": host.platform,
            }
            for host in nr.inventory.hosts.values()
        }

        return {"hosts": hosts}

    except Exception as e:
        return {"error": "inventory_error", "message": str(e)}


@mcp.tool
def get_device_data(
    target_host: str | None = None,
    getters: list[str] | None = None,
):
    """
    Generic NAPALM data collector with getter selection.
    """

    try:
        nr = init_nornir()

        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return {
                "error": "no_hosts",
                "message": f"No hosts found for target: {target_host}",
            }

        # Default getter
        if not getters:
            getters = ["facts"]

        # Validate getters
        invalid = set(getters) - ALLOWED_GETTERS.keys()
        if invalid:
            return {
                "error": "invalid_getters",
                "invalid": sorted(invalid),
                "allowed": sorted(ALLOWED_GETTERS),
            }

        result = nr.run(task=napalm_get, getters=getters)

        data = {}
        for host, task_result in result.items():
            if task_result.failed:
                data[host] = {
                    "error": "napalm_failed",
                    "message": str(task_result.exception),
                }
            else:
                data[host] = task_result.result

        return {
            "target": target_host or "all",
            "getters": getters,
            "data": data,
        }

    except Exception as e:
        return {
            "error": "execution_error",
            "message": str(e),
        }
