"""Tools module for Nornir MCP server.

This module contains the core tool definitions that are exposed to the MCP
server. It delegates execution to specific Runners (NAPALM, etc) for
performing network automation tasks.
"""

from typing import Any

from .nornir_init import nornir_manager
from .runners.napalm_runner import NapalmRunner

napalm_runner = NapalmRunner(nornir_manager)


def list_all_hosts() -> dict[str, Any]:
    """List all configured network hosts in the inventory.

    Returns:
        Dictionary containing all hosts with their basic information
        (name, IP address, platform)
    """
    try:
        nr = nornir_manager.get()

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


def get_facts(hostname: str | None = None) -> dict[str, Any]:
    """Get basic device information (vendor, model, serial, uptime).

    Args:
        hostname: Specific hostname to target, or None for all hosts

    Returns:
        Dictionary containing device facts for the targeted hosts
    """
    return napalm_runner.run_getter("facts", hostname)


def get_interfaces(hostname: str | None = None) -> dict[str, Any]:
    """Get interface details (status, speed, mac address).

    Args:
        hostname: Specific hostname to target, or None for all hosts

    Returns:
        Dictionary containing interface information for the targeted hosts
    """
    return napalm_runner.run_getter("interfaces", hostname)


def get_interfaces_ip(hostname: str | None = None) -> dict[str, Any]:
    """Get IP addresses configured on interfaces.

    Args:
        hostname: Specific hostname to target, or None for all hosts

    Returns:
        Dictionary containing interface IP information for the targeted hosts
    """
    return napalm_runner.run_getter("interfaces_ip", hostname)


def get_arp_table(hostname: str | None = None) -> dict[str, Any]:
    """Get the ARP (Address Resolution Protocol) table.

    Args:
        hostname: Specific hostname to target, or None for all hosts

    Returns:
        Dictionary containing ARP table entries for the targeted hosts
    """
    return napalm_runner.run_getter("arp_table", hostname)


def get_mac_address_table(hostname: str | None = None) -> dict[str, Any]:
    """Get the MAC address table (CAM table).

    Args:
        hostname: Specific hostname to target, or None for all hosts

    Returns:
        Dictionary containing MAC address table entries for the targeted hosts
    """
    return napalm_runner.run_getter("mac_address_table", hostname)


def reload_nornir_inventory() -> dict[str, str]:
    """Reload Nornir inventory from disk to apply changes.

    Returns:
        Dictionary indicating success or failure of the reload operation
    """
    try:
        nornir_manager.reload()
        return {
            "status": "success",
            "message": "Nornir inventory reloaded from disk.",
        }
    except Exception as e:
        return {
            "error": "reload_failed",
            "message": str(e),
        }
