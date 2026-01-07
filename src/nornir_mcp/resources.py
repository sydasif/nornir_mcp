"""Resources module for Nornir MCP server.

Provides data-centric resources for the MCP server, allowing LLMs to
inspect the environment and capabilities before taking action.
"""

from importlib import resources
from typing import Any

import yaml

from .nornir_init import nornir_manager
from .types import error_response


def get_inventory() -> dict[str, Any]:
    """Retrieve the current Nornir inventory details.

    Returns:
        Dictionary containing all hosts with their basic information
        (name, IP address, platform) and groups information.
    """
    try:
        nr = nornir_manager.get()

        # Get hosts information
        hosts = {}
        for host_name, host_obj in nr.inventory.hosts.items():
            hosts[host_name] = {
                "name": host_name,
                "ip": host_obj.hostname,
                "platform": host_obj.platform,
                "groups": [group.name for group in host_obj.groups] if host_obj.groups else [],
            }

        # Get groups information
        groups = {}
        for group_name, group_obj in nr.inventory.groups.items():
            groups[group_name] = {
                "name": group_name,
                "platform": group_obj.platform,
                "hosts": [
                    h
                    for h, host_obj in nr.inventory.hosts.items()
                    if group_name in [g.name for g in host_obj.groups]
                ],
            }

        return {"hosts": hosts, "groups": groups, "total_hosts": len(hosts), "total_groups": len(groups)}

    except Exception as e:
        return error_response("inventory_retrieval_failed", str(e))


def get_getters() -> dict[str, Any]:
    """Retrieve the supported NAPALM getters and their descriptions.

    Returns:
        Dictionary mapping getter names to human-readable descriptions.
    """
    try:
        # Use importlib.resources to access the capabilities.yaml file
        # This is more robust than Path(__file__) for packaged applications
        traversable = resources.files("nornir_mcp.data").joinpath("capabilities.yaml")

        if not traversable.is_file():
            return error_response("config_missing", "capabilities.yaml not found")

        with traversable.open() as f:
            return yaml.safe_load(f)

    except Exception as e:
        return error_response("getters_retrieval_failed", str(e))


def get_netmiko_commands() -> dict[str, Any]:
    """Retrieve the top 10 common Netmiko CLI commands and their descriptions from the capabilities YAML.

    Returns:
        Dictionary mapping command names to human-readable descriptions.
    """
    try:
        # Use importlib.resources to access the capabilities.yaml file
        traversable = resources.files("nornir_mcp.data").joinpath("capabilities.yaml")

        if not traversable.is_file():
            return error_response("config_missing", "capabilities.yaml not found")

        with traversable.open() as f:
            data = yaml.safe_load(f)

        # Return only the netmiko_commands section
        if "netmiko_commands" in data:
            return {"commands": data["netmiko_commands"]}
        else:
            return error_response(
                "netmiko_commands_not_found", "netmiko_commands section not found in capabilities.yaml"
            )

    except Exception as e:
        return error_response("netmiko_commands_retrieval_failed", str(e))
