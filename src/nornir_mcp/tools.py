"""MCP tool implementations for Nornir server.

This module provides the tool functions that are exposed to the Model Context
Protocol, allowing LLMs to interact with network devices through Nornir.
"""

import asyncio
from typing import Any

from .constants import Backend, ErrorType
from .nornir_init import get_nornir, reset_nornir
from .resources import get_inventory
from .runners.base_runner import BaseRunner
from .runners.napalm_runner import NapalmRunner
from .runners.netmiko_runner import NetmikoRunner
from .runners.paramiko_runner import ParamikoRunner
from .helpers import error_response
from .types import MCPException
from .utils import format_target, validate_target_params


async def _run_tool(
    runner_cls: type[BaseRunner],
    method_name: str,
    host_name: str | None,
    group_name: str | None,
    result_meta: dict[str, Any],
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a Nornir tool via a runner.

    Args:
        runner_cls: The runner class to instantiate
        method_name: The method name to call on the runner
        host_name: Target host name or None for all hosts
        group_name: Target group name or None for all groups
        result_meta: Metadata to include in the result
        *args: Arguments to pass to the runner method
        **kwargs: Keyword arguments to pass to the runner method

    Returns:
        Dictionary containing the tool execution results with metadata

    """
    try:
        validate_target_params(host_name, group_name)
    except ValueError as e:
        return error_response(ErrorType.INVALID_PARAMETERS, str(e))

    nr = get_nornir()
    runner = runner_cls(nr)

    try:
        method = getattr(runner, method_name)
        data = await asyncio.to_thread(method, *args, host_name=host_name, group_name=group_name, **kwargs)
        return {
            **result_meta,
            "target": format_target(host_name, group_name),
            "data": data,
        }
    except MCPException as e:
        return error_response(e.error_type, e.message)
    except Exception as e:
        return error_response(ErrorType.EXECUTION_ERROR, str(e))


async def get_device_data(
    getter: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Execute a NAPALM getter on target network devices."""
    return await _run_tool(
        NapalmRunner,
        "run_getter",
        host_name,
        group_name,
        {"backend": Backend.NAPALM, "data_type": getter},
        getter,
    )


async def run_cli_commands(
    command: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Execute a raw CLI command on target network devices using Netmiko."""
    return await _run_tool(
        NetmikoRunner,
        "run_command",
        host_name,
        group_name,
        {"backend": Backend.NETMIKO, "commands": command},
        command,
    )


async def run_shell_command(
    command: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Execute an SSH command on target Linux servers using Paramiko.

    Args:
        command: The SSH command to execute (e.g., 'ls -la', 'df -h').
        host_name: Specific host name to target.
        group_name: Specific group to target.

    """
    return await _run_tool(
        ParamikoRunner,
        "run_ssh_command",
        host_name,
        group_name,
        {"backend": Backend.PARAMIKO, "shell_command": command},
        command,
    )


async def upload_file(
    local_path: str,
    remote_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Upload a single file to network hosts using SFTP.

    Args:
        local_path: The source path on the local machine.
        remote_path: The destination path on the remote server.
        host_name: Specific host name to target.
        group_name: Specific group to target.

    """
    return await _run_tool(
        ParamikoRunner,
        "sftp_upload",
        host_name,
        group_name,
        {
            "backend": Backend.PARAMIKO,
            "operation": "upload",
            "type": "file",
            "protocol": "sftp",
            "local_path": local_path,
            "remote_path": remote_path,
        },
        local_path,
        remote_path,
    )


async def upload_directory(
    local_path: str,
    remote_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Upload a directory recursively to network hosts using SCP.

    Args:
        local_path: The source directory path on the local machine.
        remote_path: The destination directory path on the remote server.
        host_name: Specific host name to target.
        group_name: Specific group to target.

    """
    return await _run_tool(
        ParamikoRunner,
        "scp_upload_recursive",
        host_name,
        group_name,
        {
            "backend": Backend.PARAMIKO,
            "operation": "upload",
            "type": "directory",
            "protocol": "scp",
            "local_path": local_path,
            "remote_path": remote_path,
        },
        local_path,
        remote_path,
    )


async def download_file(
    remote_path: str,
    local_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Download a single file from network hosts using SFTP.

    Args:
        remote_path: The source path on the remote server.
        local_path: The destination path on the local machine.
        host_name: Specific host name to target.
        group_name: Specific group to target.

    """
    return await _run_tool(
        ParamikoRunner,
        "sftp_download",
        host_name,
        group_name,
        {
            "backend": Backend.PARAMIKO,
            "operation": "download",
            "type": "file",
            "protocol": "sftp",
            "remote_path": remote_path,
            "local_path": local_path,
        },
        remote_path,
        local_path,
    )


async def download_directory(
    remote_path: str,
    local_path: str,
    host_name: str | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """Download a directory recursively from network hosts using SCP.

    Args:
        remote_path: The source directory path on the remote server.
        local_path: The destination directory path on the local machine.
        host_name: Specific host name to target.
        group_name: Specific group to target.

    """
    return await _run_tool(
        ParamikoRunner,
        "scp_download_recursive",
        host_name,
        group_name,
        {
            "backend": Backend.PARAMIKO,
            "operation": "download",
            "type": "directory",
            "protocol": "scp",
            "remote_path": remote_path,
            "local_path": local_path,
        },
        remote_path,
        local_path,
    )


def list_nornir_inventory() -> dict[str, Any]:
    """List all configured network hosts and groups."""
    return get_inventory()


async def reload_nornir_inventory() -> dict[str, str]:
    """Reload the Nornir inventory from disk."""
    try:
        await asyncio.to_thread(reset_nornir)
        return {"status": "success", "message": "Inventory reloaded successfully"}
    except Exception as e:
        return error_response(ErrorType.RELOAD_FAILED, str(e))
