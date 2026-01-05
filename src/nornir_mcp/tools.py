"""Tools module for Nornir MCP server.

This module contains the core tool definitions for the MCP server. These functions
are designed to be registered as MCP tools to expose Nornir automation capabilities
to LLMs.
"""

import json
from typing import Literal

from nornir_napalm.plugins.tasks import napalm_get

from .constants import ALLOWED_GETTERS
from .nornir_init import get_nornir

NapalmGetter = Literal[
    "facts",
    "interfaces",
    "interfaces_ip",
    "arp_table",
    "mac_address_table",
]


def list_all_hosts():
    """List all configured network hosts in the inventory.

    Retrieves the list of network devices from the Nornir inventory, including
    their names, IP addresses, and platforms.

    Returns:
        dict: A dictionary containing a list of hosts with their details, or
              an error message if the inventory is empty or inaccessible.
    """
    try:
        nr = get_nornir()

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


def get_device_data(
    target_host: str | None = None,
    getters: list[NapalmGetter] | str | None = None,
):
    """Collect data from network devices using NAPALM getters.

    Executes specified NAPALM getters against one or all devices in the inventory.
    Allows filtering by target host and selecting specific data points to retrieve.

    Args:
        target_host (str | None): The name of a specific host to query. If None,
            queries all hosts in the inventory.
        getters (list[str] | str | None): A list of NAPALM getters to execute (e.g.,
            ['facts', 'interfaces']) or a JSON string representation of the list.
            Defaults to ['facts'] if not specified.
            See ALLOWED_GETTERS for the full list of supported getters.

    Returns:
        dict: A dictionary containing the query parameters and the results from
              each device, or error details if the operation failed.
    """
    try:
        nr = get_nornir()

        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return {
                "error": "no_hosts",
                "message": f"No hosts found for target: {target_host}",
            }

        # Parse string getters if necessary
        if isinstance(getters, str):
            try:
                getters = json.loads(getters)
            except json.JSONDecodeError:
                return {
                    "error": "invalid_format",
                    "message": "getters must be a list or a valid JSON string of a list",
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
            # Fix: task_result is a MultiResult (list-like).
            # We must access index 0 to get the actual Result object.
            if task_result.failed:
                data[host] = {
                    "error": "napalm_failed",
                    "message": str(task_result[0].exception),
                }
            else:
                data[host] = task_result[0].result

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
