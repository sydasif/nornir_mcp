"""Resources module for Nornir MCP server.

Provides data-centric resources for the MCP server, allowing LLMs to
inspect the environment and capabilities before taking action.
"""

from importlib import resources
from typing import Any

import yaml

from .nornir_init import nornir_manager
from .types import error_response


def get_inventory() -> dict[str, Any]:
    """Retrieve the current Nornir inventory details.

    Returns:
        Dictionary containing all hosts with their basic information
        (name, IP address, platform).
    """
    try:
        nr = nornir_manager.get()

        if not nr.inventory.hosts:
            return {"hosts": {}}

        hosts = {
            host.name: {
                "name": host.name,
                "ip": host.hostname,
                "platform": host.platform,
            }
            for host in nr.inventory.hosts.values()
        }

        return {"hosts": hosts}

    except Exception as e:
        return error_response("inventory_retrieval_failed", str(e))


def get_capabilities() -> dict[str, Any]:
    """Retrieve the supported NAPALM getters and their descriptions.

    Returns:
        Dictionary mapping getter names to human-readable descriptions.
    """
    try:
        # Use importlib.resources to access the capabilities.yaml file
        # This is more robust than Path(__file__) for packaged applications
        traversable = resources.files("nornir_mcp.data").joinpath("capabilities.yaml")

        if not traversable.is_file():
            return error_response("config_missing", "capabilities.yaml not found")

        with traversable.open() as f:
            return yaml.safe_load(f)

    except Exception as e:
        return error_response("capabilities_retrieval_failed", str(e))
