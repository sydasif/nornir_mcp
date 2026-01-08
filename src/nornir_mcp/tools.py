"""MCP tool implementations for Nornir server.

This module provides the tool functions that are exposed to the Model Context
Protocol, allowing LLMs to interact with network devices through Nornir.

All tools follow a consistent pattern: validate input, execute using appropriate
runner, and return standardized success or error responses.
"""

import asyncio
from typing import Any

from .constants import Backend, ErrorType
from .nornir_init import get_nornir, reset_nornir
from .resources import get_inventory
from .runners.napalm_runner import NapalmRunner
from .runners.netmiko_runner import NetmikoRunner
from .runners.paramiko_runner import ParamikoRunner
from .types import MCPException, error_response
from .utils import format_target, validate_target_params


async def run_napalm_getter(
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
            Can be any NAPALM-compliant getter string, not just those in the resource list.
            The server validates this at runtime.
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

    nr = get_nornir()
    runner = NapalmRunner(nr)
    try:
        data = await asyncio.to_thread(runner.run_getter, getter, host_name, group_name)
        return {
            "backend": Backend.NAPALM,
            "getter": getter,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def run_netmiko_command(
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
            Warning: If the server is in READ_ONLY_MODE, dangerous configuration commands will be blocked.
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

    nr = get_nornir()
    runner = NetmikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.run_command, command, host_name, group_name)
        return {
            "backend": Backend.NETMIKO,
            "command": command,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


def list_nornir_inventory() -> dict[str, Any]:
    """List all configured network hosts and groups.

    Returns comprehensive inventory information including host names,
    IP addresses, platforms, and group memberships.

    Returns:
        Dictionary containing hosts, groups, and counts.
        On error, returns an error response with 'error' and 'message' keys.
    """
    return get_inventory()


async def reload_nornir_inventory() -> dict[str, str]:
    """Reload the Nornir inventory from disk.

    Forces a reload of the inventory configuration without restarting
    the server. Use this after editing inventory files to apply changes.

    Returns:
        Dictionary with 'status' and 'message' on success,
        or an error response with 'error' and 'message' on failure.
    """
    try:
        await asyncio.to_thread(reset_nornir)
        return {"status": "success", "message": "Inventory reloaded successfully"}
    except Exception as e:
        return error_response(ErrorType.RELOAD_FAILED, str(e))


async def run_paramiko_command(
    command: str,
    host_name: str | None = None,
    group_name: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute an SSH command on target Linux servers using Paramiko.

    Runs a command on specified Linux servers via SSH and returns the output.

    Args:
        command: The SSH command to execute (e.g., 'ls -la', 'df -h', 'systemctl status nginx').
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.
        timeout: Command execution timeout in seconds (default: 30)

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
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

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.run_ssh_command, command, host_name, group_name, timeout)
        return {
            "backend": Backend.PARAMIKO,
            "command": command,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_sftp_upload(
    local_path: str,
    remote_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Upload a file to target Linux servers via SFTP using Paramiko.

    Uploads a local file to specified Linux servers via SFTP.

    Args:
        local_path: Path to the local file to upload
        remote_path: Destination path on the remote servers
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - local_path (str): Path of the local file that was uploaded
            - remote_path (str): Destination path on remote servers
            - target (str): Description of targeted hosts
            - data (dict): Upload results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.sftp_upload, local_path, remote_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "local_path": local_path,
            "remote_path": remote_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_sftp_download(
    remote_path: str,
    local_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Download a file from target Linux servers via SFTP using Paramiko.

    Downloads a file from specified Linux servers via SFTP.

    Args:
        remote_path: Path to the remote file to download
        local_path: Destination path for the downloaded file (directory for multiple hosts)
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - remote_path (str): Path of the remote file that was downloaded
            - local_path (str): Destination path for the downloaded file
            - target (str): Description of targeted hosts
            - data (dict): Download results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.sftp_download, remote_path, local_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "remote_path": remote_path,
            "local_path": local_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_sftp_list(
    remote_path: str = ".",
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """List files and directories in a remote path via SFTP using Paramiko.

    Lists the contents of a directory on specified Linux servers via SFTP.

    Args:
        remote_path: Remote directory path to list (default: current directory)
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - remote_path (str): Path of the remote directory that was listed
            - target (str): Description of targeted hosts
            - data (dict): File listing results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.sftp_list, remote_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "remote_path": remote_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_scp_upload(
    local_path: str,
    remote_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Upload a file to target Linux servers via SCP using Paramiko.

    Uploads a local file to specified Linux servers via SCP.

    Args:
        local_path: Path to the local file to upload
        remote_path: Destination path on the remote servers
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - local_path (str): Path of the local file that was uploaded
            - remote_path (str): Destination path on remote servers
            - target (str): Description of targeted hosts
            - data (dict): Upload results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.scp_upload, local_path, remote_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "local_path": local_path,
            "remote_path": remote_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_scp_download(
    remote_path: str,
    local_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Download a file from target Linux servers via SCP using Paramiko.

    Downloads a file from specified Linux servers via SCP.

    Args:
        remote_path: Path to the remote file to download
        local_path: Destination path for the downloaded file (directory for multiple hosts)
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - remote_path (str): Path of the remote file that was downloaded
            - local_path (str): Destination path for the downloaded file
            - target (str): Description of targeted hosts
            - data (dict): Download results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.scp_download, remote_path, local_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "remote_path": remote_path,
            "local_path": local_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def paramiko_scp_upload_recursive(
    local_path: str,
    remote_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Upload a directory to target Linux servers via SCP using Paramiko recursively.

    Uploads a local directory to specified Linux servers via SCP recursively.

    Args:
        local_path: Path to the local directory to upload
        remote_path: Destination path on the remote servers
        host_name: Specific host name to target. If omitted, targets all hosts.
            Cannot be used with group_name.
        group_name: Specific group to target. If omitted, targets all hosts.
            Cannot be used with host_name.

    Returns:
        On success: A dictionary with keys:
            - backend (str): Always "paramiko"
            - local_path (str): Path of the local directory that was uploaded
            - remote_path (str): Destination path on remote servers
            - target (str): Description of targeted hosts
            - data (dict): Upload results keyed by hostname

        On error: A dictionary with 'error' and 'message' keys.

    Raises:
        ValueError: If both host_name and group_name are specified.
    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = ParamikoRunner(nr)
    try:
        data = await asyncio.to_thread(runner.scp_upload_recursive, local_path, remote_path, host_name, group_name)
        return {
            "backend": Backend.PARAMIKO,
            "local_path": local_path,
            "remote_path": remote_path,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))