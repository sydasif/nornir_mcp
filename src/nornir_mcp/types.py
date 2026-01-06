from typing_extensions import TypedDict


class MCPError(TypedDict):
    error: str
    message: str


def error_response(error_type: str, message: str) -> MCPError:
    """Create a standardized MCP error response.

    Args:
        error_type: The type of error (e.g., 'not_found')
        message: Descriptive error message

    Returns:
        MCPError TypedDict
    """
    return {"error": error_type, "message": message}
