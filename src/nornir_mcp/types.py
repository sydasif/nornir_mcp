from typing import Any

from typing_extensions import TypedDict


class MCPError(TypedDict):
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


def error_response(error_type: str, message: str) -> MCPError:
    """Create a standardized MCP error response.

    Args:
        error_type: The type of error (e.g., 'not_found').
        message: Descriptive error message.

    Returns:
        A dictionary with error and message keys.

    Example:
        >>> error_response("not_found", "Host not found")
        {'error': 'not_found', 'message': 'Host not found'}
    """
    return {"error": error_type, "message": message}
