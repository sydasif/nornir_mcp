"""Tools module for Nornir MCP server.

This module contains the core tool definitions.
It delegates execution to specific Runners (NAPALM, etc).
"""

from typing import Any

from .nornir_init import nornir_manager
from .runners.napalm_runner import NapalmRunner

# Initialize the runner with the manager singleton
napalm_runner = NapalmRunner(nornir_manager)


def list_all_hosts() -> dict[str, Any]:
    """List all configured network hosts in the inventory."""
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
    """Get basic device information (vendor, model, serial, uptime)."""
    return napalm_runner.run_getter("facts", hostname)


def get_interfaces(hostname: str | None = None) -> dict[str, Any]:
    """Get interface details (status, speed, mac address)."""
    return napalm_runner.run_getter("interfaces", hostname)


def get_interfaces_ip(hostname: str | None = None) -> dict[str, Any]:
    """Get IP addresses configured on interfaces."""
    return napalm_runner.run_getter("interfaces_ip", hostname)


def get_arp_table(hostname: str | None = None) -> dict[str, Any]:
    """Get the ARP (Address Resolution Protocol) table."""
    return napalm_runner.run_getter("arp_table", hostname)


def get_mac_address_table(hostname: str | None = None) -> dict[str, Any]:
    """Get the MAC address table (CAM table)."""
    return napalm_runner.run_getter("mac_address_table", hostname)


def reload_nornir_inventory() -> dict[str, str]:
    """Reload Nornir inventory from disk to apply changes."""
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
