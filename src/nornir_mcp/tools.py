"""MCP tool implementations for Nornir server.

This module provides the tool functions that are exposed to the Model Context
Protocol, allowing LLMs to interact with network devices through Nornir.

All tools follow a consistent pattern: validate input, execute using appropriate
runner, and return standardized success or error responses.
"""

from typing import Any

from .constants import Backend, ErrorType
from .nornir_init import NornirManager
from .resources import get_inventory
from .result import Success
from .runners.napalm_runner import NapalmRunner
from .runners.netmiko_runner import NetmikoRunner
from .types import error_response
from .utils import format_target, validate_target_params


def run_napalm_getter(
    getter: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Execute a NAPALM getter on target network devices.

    Runs a specified NAPALM getter function on one or more network devices
    to retrieve structured, normalized data from network devices across
    different vendor platforms.

    Args:
        getter: The getter to execute (e.g., 'facts', 'interfaces', 'config').
            Check the 'nornir://napalm_getters' resource for supported getters.
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "napalm"
            - getter (str): The getter that was executed
            - target (str): Description of targeted hosts
            - data (dict): Retrieved data keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    runner = NapalmRunner(NornirManager.instance())
    result = runner.run_getter(getter, host_name, group_name)

    if isinstance(result, Success):
        return {
            "backend": Backend.NAPALM.value,
            "getter": getter,
            "target": format_target(host_name, group_name),
            "data": result.value,
        }
    else:
        # result is Error
        return error_response(result.error_type, result.message)


def run_netmiko_command(
    command: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Execute a raw CLI command on target network devices using Netmiko.

    Sends a command to the specified devices and returns the raw output.
    This is useful for commands that are not available as NAPALM getters
    or for vendor-specific operations.

    Args:
        command: The CLI command to execute (e.g., 'show version').
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "netmiko"
            - command (str): The command that was executed
            - target (str): Description of targeted hosts
            - data (dict): Command output keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    runner = NetmikoRunner(NornirManager.instance())
    result = runner.run_command(command, host_name, group_name)

    if isinstance(result, Success):
        return {
            "backend": Backend.NETMIKO.value,
            "command": command,
            "target": format_target(host_name, group_name),
            "data": result.value,
        }
    else:
        # result is Error
        return error_response(result.error_type, result.message)


def list_nornir_inventory() -> dict[str, Any]:
    """List all configured network hosts and groups.

    Returns comprehensive inventory information including host names,
    IP addresses, platforms, and group memberships.

    Returns:
        Dictionary containing hosts, groups, and counts.
        On error, returns an error response with 'error' and 'message' keys.
    """
    return get_inventory()


def reload_nornir_inventory() -> dict[str, str]:
    """Reload the Nornir inventory from disk.

    Forces a reload of the inventory configuration without restarting
    the server. Use this after editing inventory files to apply changes.

    Returns:
        Dictionary with 'status' and 'message' on success,
        or an error response with 'error' and 'message' on failure.
    """
    try:
        NornirManager.instance().reload()
        return {"status": "success", "message": "Inventory reloaded successfully"}
    except Exception as e:
        return error_response(ErrorType.RELOAD_FAILED, str(e))
