"""Tools module for Nornir MCP server.

This module contains the core tool definitions for the MCP server.
It uses specific functions for each NAPALM getter to ensure high reliability with LLMs.
"""

from nornir_napalm.plugins.tasks import napalm_get

from .nornir_init import nornir_manager


def list_all_hosts():
    """List all configured network hosts in the inventory.

    Returns:
        dict: A dictionary containing a list of hosts with their details.
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


def _run_napalm_getter(getter: str, hostname: str | None = None):
    """Helper function to run a specific NAPALM getter."""
    try:
        nr = nornir_manager.get()

        if hostname:
            nr = nr.filter(name=hostname)

        if not nr.inventory.hosts:
            return {
                "error": "no_hosts",
                "message": f"No hosts found for target: {hostname or 'all'}",
            }

        # Run the specific getter
        result = nr.run(task=napalm_get, getters=[getter])

        data = {}
        for host, task_result in result.items():
            # task_result is a MultiResult (list-like)
            # Access [0] to get the actual Result object
            actual_result = task_result[0]

            if actual_result.failed:
                data[host] = {
                    "error": "napalm_failed",
                    "message": str(actual_result.exception),
                }
            else:
                # The result is nested in a dict keyed by the getter name
                # e.g. {'facts': {...}} -> we want just the inner {...}
                res = actual_result.result
                data[host] = res.get(getter) if isinstance(res, dict) else res

        return {
            "getter": getter,
            "target": hostname or "all",
            "data": data,
        }

    except Exception as e:
        return {
            "error": "execution_error",
            "message": str(e),
        }


def get_facts(hostname: str | None = None):
    """Get basic device information (vendor, model, serial, uptime)."""
    return _run_napalm_getter("facts", hostname)


def get_interfaces(hostname: str | None = None):
    """Get interface details (status, speed, mac address)."""
    return _run_napalm_getter("interfaces", hostname)


def get_interfaces_ip(hostname: str | None = None):
    """Get IP addresses configured on interfaces."""
    return _run_napalm_getter("interfaces_ip", hostname)


def get_arp_table(hostname: str | None = None):
    """Get the ARP (Address Resolution Protocol) table."""
    return _run_napalm_getter("arp_table", hostname)


def get_mac_address_table(hostname: str | None = None):
    """Get the MAC address table (CAM table)."""
    return _run_napalm_getter("mac_address_table", hostname)


def reload_nornir_inventory():
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
