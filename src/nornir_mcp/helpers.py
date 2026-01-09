"""Consolidated helper functions for the Nornir MCP server.

This module contains all shared helper functions used across multiple modules
to reduce code duplication and improve maintainability.
"""

from .constants import ErrorType, TargetType
from .types import error_response, MCPException, MCPError
from typing import Any
import tarfile
import os
from pathlib import Path


def format_target(host_name: str | None, group_name: str | None) -> str:
    """Format target description based on filtering parameters.

    Args:
        host_name: Specific host name to target
        group_name: Specific group to target

    Returns:
        Formatted target string

    Examples:
        >>> format_target("router-01", None)
        'router-01'
        >>> format_target(None, "core")
        'group:core'
        >>> format_target(None, None)
        'all'

    """
    if host_name:
        return host_name
    if group_name:
        return f"{TargetType.GROUP}:{group_name}"
    return TargetType.ALL


def validate_target_params(host_name: str | None, group_name: str | None) -> None:
    """Validate that only one target parameter is specified.

    Args:
        host_name: Specific host name to target
        group_name: Specific group to target

    Raises:
        ValueError: If both host_name and group_name are specified

    Examples:
        >>> validate_target_params("host1", None)  # OK
        >>> validate_target_params(None, "group1")  # OK
        >>> validate_target_params("host1", "group1")  # Raises ValueError

    """
    if host_name and group_name:
        raise ValueError("Cannot specify both host_name and group_name")


def extract_single_key(data: Any, key: str) -> Any:
    """Extract a single key from a dictionary.

    Utility function to safely extract a specific key from nested data structures.

    Args:
        data: Dictionary or other data structure to extract from
        key: Key to extract from the data structure

    Returns:
        Value of the key if it exists in the dictionary, otherwise returns the original data

    Example:
        >>> extract_single_key({"a": 1, "b": 2}, "a")
        1
        >>> extract_single_key([1, 2, 3], "a")
        [1, 2, 3]
    """
    if isinstance(data, dict) and key in data:
        return data[key]
    return data


def extract_generic_data(task_output: Any) -> Any:
    """Generic extractor that returns the input unchanged.

    Args:
        task_output: Raw output from any task

    Returns:
        The same input unchanged (passthrough extractor)
    """
    return task_output


# Keep backward compatibility for existing code
def extract_ssh_data(task_output: Any) -> Any:
    """Extract data from SSH command results.

    Args:
        task_output: Raw output from SSH command task

    Returns:
        Extracted data from the SSH command result
    """
    return extract_generic_data(task_output)


def extract_upload_data(task_output: Any) -> Any:
    """Extract data from file upload results.

    Args:
        task_output: Raw output from file upload task

    Returns:
        Extracted data from the upload result
    """
    return extract_generic_data(task_output)


def extract_download_data(task_output: Any) -> Any:
    """Extract data from file download results.

    Args:
        task_output: Raw output from file download task

    Returns:
        Extracted data from the download result
    """
    return extract_generic_data(task_output)


def is_safe_extract(member: tarfile.TarInfo, extract_path: str) -> bool:
    """Check if a tarfile member is safe to extract (prevents path traversal).

    Args:
        member: TarInfo object representing a file in the tar archive
        extract_path: Path where the archive will be extracted

    Returns:
        True if the member is safe to extract, False otherwise
    """
    import os
    # Get the resolved path after joining
    resolved_path = os.path.realpath(os.path.join(extract_path, member.name))

    # Get the resolved extract path
    resolved_extract_path = os.path.realpath(extract_path)

    # Check if the resolved path starts with the extract path
    # This prevents path traversal attacks
    return resolved_path.startswith(resolved_extract_path)


def validate_file_operation_params(local_path: str | None, remote_path: str | None, path_type: str = "file") -> None:
    """Validate parameters for file operations.

    Args:
        local_path: Local file or directory path
        remote_path: Remote file or directory path
        path_type: Type of path ("file" or "directory") for error messages

    Raises:
        ValueError: If parameters are invalid
    """
    if not local_path:
        raise ValueError("Local path parameter is required")
    if not remote_path:
        raise ValueError("Remote path parameter is required")

    if path_type == "file" and not os.path.exists(local_path):
        raise ValueError(f"Local {path_type} does not exist: {local_path}")
    elif path_type == "directory" and not os.path.exists(local_path):
        raise ValueError(f"Local {path_type} does not exist: {local_path}")


