"""Resources module for Nornir MCP server.

Provides data-centric resources for the MCP server, allowing LLMs to
inspect the environment and capabilities before taking action.

This module contains functions that return structured data about
network device capabilities and inventory information. The resources
are designed to be consumed by Language Learning Models (LLMs) to
understand what operations are possible before executing network tasks.

Example:
    Get available NAPALM getters::

        from nornir_mcp.resources import get_getters
        getters = get_getters()

"""

from functools import lru_cache
from importlib import resources
from typing import Any

import yaml

from .constants import ConfigKey, DefaultValue, ErrorType
from .nornir_init import get_nornir
from .types import error_response


def get_inventory() -> dict[str, Any]:
    """Retrieve the current Nornir inventory details.

    Fetches comprehensive information about all configured network hosts
    and groups from the Nornir inventory. This includes host names,
    IP addresses, platform types, and group memberships.

    Returns:
        Dictionary containing all hosts with their basic information
        (name, IP address, platform) and groups information.

        The returned dictionary has the format:
        {
            "hosts": {
                "hostname": {
                    "name": str,
                    "ip": str,
                    "platform": str,
                    "groups": list[str]
                }
            },
            "groups": {
                "groupname": {
                    "name": str,
                    "platform": str,
                    "hosts": list[str]
                }
            },
            "total_hosts": int,
            "total_groups": int
        }

    Raises:
        Exception: If inventory retrieval fails due to configuration issues

    """
    try:
        nr = get_nornir()

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
        return error_response(ErrorType.INVENTORY_RETRIEVAL_FAILED, str(e))


@lru_cache(maxsize=1)
def _load_capabilities() -> dict[str, Any]:
    """Load and cache capabilities YAML (thread-safe).

    This function loads the capabilities.yaml file once and caches the result
    to avoid repeated file system operations. The cache is thread-safe due to
    the GIL protecting the function execution.

    Returns:
        The parsed capabilities YAML data as a dictionary.

    Raises:
        Exception: If capabilities.yaml file is not found or cannot be read

    """
    # Use importlib.resources to access the capabilities.yaml file
    # This is more robust than Path(__file__) for packaged applications
    traversable = resources.files("nornir_mcp.data").joinpath(DefaultValue.CAPABILITIES_FILENAME)

    if not traversable.is_file():
        raise FileNotFoundError(f"{DefaultValue.CAPABILITIES_FILENAME} not found")

    with traversable.open() as f:
        return yaml.safe_load(f)


def get_getters() -> dict[str, Any]:
    """Retrieve the supported NAPALM getters and their descriptions.

    Fetches all available NAPALM getters from the capabilities.yaml file.
    These getters represent the various types of data that can be retrieved
    from network devices using the NAPALM library.

    **IMPORTANT:** This list is provided as a guide and is NOT exhaustive.
    If a user requests a specific getter not in this list, attempt to run it.
    The server will validate it dynamically.

    Returns:
        Dictionary mapping getter names to human-readable descriptions.
        The format is {"getters": {"getter_name": "description", ...}}.

    Example:
            {
                "getters": {
                    "facts": "Retrieved device information...",
                    "interfaces": "Retrieved interface details..."
                }
            }

    Raises:
        Exception: If capabilities.yaml file is not found or cannot be read

    """
    try:
        capabilities = _load_capabilities()
        # Return only the getters section
        if ConfigKey.GETTERS in capabilities:
            return {"getters": capabilities[ConfigKey.GETTERS]}
        else:
            return error_response(
                ErrorType.GETTERS_NOT_FOUND,
                f"{ConfigKey.GETTERS} section not found in {DefaultValue.CAPABILITIES_FILENAME}",
            )
    except Exception as e:
        return error_response(ErrorType.GETTERS_RETRIEVAL_FAILED, str(e))


def get_netmiko_commands() -> dict[str, Any]:
    """Retrieve the top 10 common Netmiko CLI commands and their descriptions from the capabilities YAML.

    Fetches common network CLI commands that can be executed on devices
    using the Netmiko library. These commands represent frequently used
    operational commands for network device interaction.

    Returns:
        Dictionary mapping command names to human-readable descriptions.
        The format is {"commands": {"command_name": "description", ...}}.

    Example:
            {
                "commands": {
                    "show version": "Display device version and system information",
                    "show running-config": "Display current device configuration"
                }
            }

    Raises:
        Exception: If capabilities.yaml file is not found or cannot be read

    """
    try:
        capabilities = _load_capabilities()
        # Return only the netmiko_commands section
        if ConfigKey.NETMIKO_COMMANDS in capabilities:
            return {"commands": capabilities[ConfigKey.NETMIKO_COMMANDS]}
        else:
            return error_response(
                ErrorType.NETMIKO_COMMANDS_NOT_FOUND,
                f"{ConfigKey.NETMIKO_COMMANDS} section not found in {DefaultValue.CAPABILITIES_FILENAME}",
            )

    except Exception as e:
        return error_response(ErrorType.NETMIKO_COMMANDS_RETRIEVAL_FAILED, str(e))
