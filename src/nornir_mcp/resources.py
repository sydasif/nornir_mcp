"""Resources module for Nornir MCP server.

This module contains resource definitions that can be exposed via the MCP server.
Resources provide read-only access to static or dynamic data.
"""

from .constants import ALLOWED_GETTERS


def napalm_getters():
    """Return the list of allowed NAPALM getters.

    This resource provides a list of valid getter names that can be used with
    the `get_device_data` tool, along with their descriptions.

    Returns:
        dict: A dictionary mapping getter names to their descriptions.
    """
    return {"napalm_getters": ALLOWED_GETTERS}
