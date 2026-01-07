"""Tools module for Nornir MCP server.

This module contains the core tool definitions that are exposed to the MCP
server. It delegates execution to specific Runners (NAPALM, Netmiko) for
performing network automation tasks.
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
    """Generic tool to run a getter on a network device using NAPALM.

    Args:
        getter: The getter to execute (check mcp resource capabilities for supported getters)
        host_name: (Optional) Specific host name to target. Omit to target ALL hosts.
        group_name: (Optional) Specific group to target. Cannot be used with host_name.

    Returns:
        Dictionary containing the results of the getter execution
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
    """Run a CLI command on network devices using Netmiko.

    Args:
        command: The command to execute
        host_name: (Optional) Specific host name to target. Omit to target ALL hosts.
        group_name: (Optional) Specific group to target. Cannot be used with host_name.

    Returns:
        Dictionary containing the command results
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
    """List all configured network hosts in the inventory.

    Returns:
        Dictionary containing all hosts or MCPError
    """
    return get_inventory()


def reload_nornir_inventory() -> dict[str, str] | MCPError:
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
        return error_response("reload_failed", str(e))