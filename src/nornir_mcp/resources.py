"""Resources module for Nornir MCP server.

Provides data-centric resources for the MCP server, allowing LLMs to
inspect the environment and capabilities before taking action.
"""

from pathlib import Path
from typing import Any

import yaml

from .nornir_init import nornir_manager


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
        return {"error": "inventory_retrieval_failed", "message": str(e)}


def get_capabilities() -> dict[str, Any]:
    """Retrieve the supported NAPALM getters and their descriptions.

    Returns:
        Dictionary mapping getter names to human-readable descriptions.
    """
    try:
        # Resolve path to capabilities.yaml
        current_dir = Path(__file__).parent
        yaml_path = current_dir / "data" / "capabilities.yaml"

        if not yaml_path.exists():
            return {"error": "config_missing", "message": "capabilities.yaml not found"}

        with open(yaml_path) as f:
            return yaml.safe_load(f)

    except Exception as e:
        return {"error": "capabilities_retrieval_failed", "message": str(e)}
