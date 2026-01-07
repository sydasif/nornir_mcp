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

from .constants import Backend, ErrorType
from .nornir_init import NornirManager
from .resources import get_getters, get_inventory, get_netmiko_commands
from .runners.napalm_runner import NapalmRunner
from .runners.netmiko_runner import NetmikoRunner
from .types import MCPError, NapalmResult, NetmikoResult, error_response
from .utils import format_target, validate_target_params


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
    try:
        validate_target_params(host_name, group_name)

        # Validate getter name against capabilities
        valid_getters_data = get_getters()
        if isinstance(valid_getters_data, dict) and "getters" in valid_getters_data:
            valid_getters = valid_getters_data["getters"]
            if getter not in valid_getters:
                return error_response(
                    ErrorType.INVALID_GETTER,
                    f"Unknown getter '{getter}'. Valid getters: {', '.join(valid_getters.keys())}",
                )
        else:
            # If we can't validate, warn but continue (fail gracefully)
            pass

        manager = NornirManager.instance()
        runner = NapalmRunner(manager)
        result = runner.run_getter(getter, host_name, group_name)

        # Handle the Result type
        if result.is_error():
            # Convert the Result error to MCPError format
            return error_response(result.error_type, result.message)

        target = format_target(host_name, group_name)
        raw_data = result.unwrap()

        return {
            "backend": Backend.NAPALM.value,
            "getter": getter,
            "target": target,
            "data": raw_data,
        }
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))
    except Exception as e:
        return error_response(ErrorType.TOOL_ERROR, str(e))


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
    try:
        validate_target_params(host_name, group_name)

        # Validate command to prevent potentially dangerous inputs
        # Commands should be non-empty and not contain dangerous characters like semicolons or pipes
        if not command or not isinstance(command, str):
            return error_response(ErrorType.INVALID_COMMAND, "Command must be a non-empty string")

        # Basic validation to prevent command injection
        dangerous_patterns = [";", "&&", "||", "|", "`", "$("]
        for pattern in dangerous_patterns:
            if pattern in command:
                return error_response(
                    ErrorType.INVALID_COMMAND,
                    f"Command contains potentially dangerous character sequence: {pattern}",
                )

        valid_commands_data = get_netmiko_commands()
        if isinstance(valid_commands_data, dict) and "commands" in valid_commands_data:
            # We don't fail validation for unknown commands as users may need to run custom commands
            pass
        else:
            # If we can't validate, continue anyway
            pass

        manager = NornirManager.instance()
        runner = NetmikoRunner(manager)
        result = runner.run_command(command, host_name, group_name)

        # Handle the Result type
        if result.is_error():
            # Convert the Result error to MCPError format
            return error_response(result.error_type, result.message)

        target = format_target(host_name, group_name)
        raw_data = result.unwrap()

        return {
            "backend": Backend.NETMIKO.value,
            "command": command,
            "target": target,
            "data": raw_data,
        }
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))
    except Exception as e:
        return error_response(ErrorType.TOOL_ERROR, str(e))


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
        manager = NornirManager.instance()
        manager.reload()
        return {
            "status": "success",
            "message": "Nornir inventory reloaded from disk.",
        }
    except Exception as e:
        return error_response(ErrorType.RELOAD_FAILED, str(e))
