"""Type definitions and exception classes for the Nornir MCP server.

This module contains custom exception classes and type definitions
used throughout the application for consistent error handling and data structures.
"""

from typing import Any

from typing_extensions import TypedDict

from .constants import ErrorType


class MCPException(Exception):
    """Custom exception for MCP errors."""

    def __init__(self, error_type: str, message: str):
        """Initialize the MCP exception.

        Args:
            error_type: The type of error as a string
            message: Human-readable error message

        """
        self.error_type = error_type
        self.message = message
        super().__init__(f"{error_type}: {message}")


class MCPError(TypedDict):
    """Standardized error response format for MCP operations.

    Attributes:
        error: Error type identifier
        message: Human-readable error description

    """

    error: str
    message: str


class NapalmResult(TypedDict):
    """Standardized successful result for a NAPALM getter execution."""

    backend: str
    getter: str
    target: str
    data: dict[str, Any]


class NetmikoResult(TypedDict):
    """Standardized successful result for a Netmiko command execution."""

    backend: str
    command: str
    target: str
    data: dict[str, Any]


def error_response(error_type: ErrorType | str, message: str) -> MCPError:
    """Create a standardized MCP error response.

    Args:
        error_type: The type of error - accepts ErrorType enum or string
        message: Descriptive error message

    Returns:
        A dictionary with error and message keys

    Example:
        >>> error_response(ErrorType.NOT_FOUND, "Host not found")
        {'error': 'not_found', 'message': 'Host not found'}
        >>> error_response("not_found", "Host not found")
        {'error': 'not_found', 'message': 'Host not found'}

    """
    # Convert to string (works with StrEnum, str, or other types)
    error_str = str(error_type)
    return {"error": error_str, "message": message}
