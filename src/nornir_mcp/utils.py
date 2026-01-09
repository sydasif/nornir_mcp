"""Utility functions for the Nornir MCP server.

This module contains shared helper functions used across multiple modules
to reduce code duplication and improve maintainability.
"""

from typing import Any

from .constants import TargetType


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
