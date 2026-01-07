"""Tools module for Nornir MCP server.

This module contains the core tool definitions that are exposed to the MCP
server. It delegates execution to specific Runners (NAPALM, Netmiko) for
performing network automation tasks.

The tools provide standardized interfaces for common network automation
operations, allowing LLMs to interact with network devices through
well-defined functions. Each tool handles error responses consistently
and provides structured output.

Example:
    Execute a NAPALM getter::

        result = run_napalm_getter(getter="facts", host_name="router-01")

    Execute a Netmiko command::

        result = run_netmiko_command(command="show version", group_name="core")
"""

from typing import Any

from .nornir_init import nornir_manager
from .resources import get_inventory
from .runners.napalm_runner import NapalmRunner
from .runners.netmiko_runner import NetmikoRunner
from .types import MCPError, NapalmResult, NetmikoResult, error_response


def run_napalm_getter(
    getter: str, host_name: str | None = None, group_name: str | None = None
) -> NapalmResult | MCPError:
    """Execute a NAPALM getter on target network devices.

    Runs a specified NAPALM getter function on one or more network devices.
    This provides structured, normalized data from network devices across
    different vendor platforms.

    Args:
        getter: The getter to execute (check mcp resource napalm_getters for supported getters)
        host_name: (Optional) Specific host name to target. Omit to target ALL hosts.
        group_name: (Optional) Specific group to target. Cannot be used with host_name.

    Returns:
        NapalmResult containing the getter results and metadata, or MCPError
        if the operation fails.

        The result format is:
        {
            "backend": "napalm",
            "getter": str,
            "target": str,
            "data": dict
        }

    Raises:
        ValueError: If both host_name and group_name are specified
        Exception: If the NAPALM getter execution fails
    """
    if host_name and group_name:
        return error_response("invalid_parameters", "Cannot specify both host_name and group_name")

    try:
        runner = NapalmRunner(nornir_manager)
        raw_result = runner.run_getter(getter, host_name, group_name)

        # Check if runner returned an error
        if isinstance(raw_result, dict) and "error" in raw_result:
            return raw_result  # Already formatted as MCPError

        if host_name:
            target = host_name
        elif group_name:
            target = f"group:{group_name}"
        else:
            target = "all"

        return {
            "backend": "napalm",
            "getter": getter,
            "target": target,
            "data": raw_result,
        }
    except Exception as e:
        return error_response("tool_error", str(e))


def run_netmiko_command(
    command: str, host_name: str | None = None, group_name: str | None = None
) -> NetmikoResult | MCPError:
    """Execute a CLI command on target network devices using Netmiko.

    Runs a raw CLI command on one or more network devices using the Netmiko
    library. This provides direct access to device command-line interfaces
    and returns the raw command output.

    Args:
        command: The command to execute
        host_name: (Optional) Specific host name to target. Omit to target ALL hosts.
        group_name: (Optional) Specific group to target. Cannot be used with host_name.

    Returns:
        NetmikoResult containing the command results and metadata, or MCPError
        if the operation fails.

        The result format is:
        {
            "backend": "netmiko",
            "command": str,
            "target": str,
            "data": dict
        }

    Raises:
        ValueError: If both host_name and group_name are specified
        Exception: If the Netmiko command execution fails
    """
    if host_name and group_name:
        return error_response("invalid_parameters", "Cannot specify both host_name and group_name")

    try:
        runner = NetmikoRunner(nornir_manager)
        raw_result = runner.run_command(command, host_name, group_name)

        # Check if runner returned an error
        if isinstance(raw_result, dict) and "error" in raw_result:
            return raw_result  # Already formatted as MCPError

        if host_name:
            target = host_name
        elif group_name:
            target = f"group:{group_name}"
        else:
            target = "all"

        return {
            "backend": "netmiko",
            "command": command,
            "target": target,
            "data": raw_result,
        }
    except Exception as e:
        return error_response("tool_error", str(e))


def list_nornir_inventory() -> dict[str, Any] | MCPError:
    """List all configured network hosts in the Nornir inventory.

    Retrieves comprehensive information about all network devices
    and groups configured in the Nornir inventory. This provides
    an overview of the managed network infrastructure.

    Returns:
        Dictionary containing all hosts and groups information,
        or MCPError if inventory retrieval fails.

        The result format is:
        {
            "hosts": dict,
            "groups": dict,
            "total_hosts": int,
            "total_groups": int
        }

    Raises:
        Exception: If inventory retrieval fails
    """
    return get_inventory()


def reload_nornir_inventory() -> dict[str, str] | MCPError:
    """Reload Nornir inventory from disk to apply changes.

    Forces the Nornir manager to reload the inventory configuration
    from disk, picking up any changes made to inventory files since
    the server started. This is useful when inventory files are
    modified and changes need to be applied without restarting the server.

    Returns:
        Dictionary indicating success or failure of the reload operation.

        Success format:
        {
            "status": "success",
            "message": "Nornir inventory reloaded from disk."
        }

        Error format:
        MCPError with error details

    Raises:
        Exception: If inventory reload fails
    """
    try:
        nornir_manager.reload()
        return {
            "status": "success",
            "message": "Nornir inventory reloaded from disk.",
        }
    except Exception as e:
        return error_response("reload_failed", str(e))
