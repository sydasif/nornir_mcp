"""Nornir initialization module for Model Context Protocol (MCP) server.

This module handles the initialization of the Nornir framework with a
singleton pattern to ensure consistent state across the MCP server
instance. It loads inventory configuration from environment-specified
paths for hosts, groups, and defaults files.
"""

import os

from nornir import InitNornir

_nr_instance = None


def init_nornir():
    """Initialize or return the existing Nornir instance using singleton pattern.

    Creates a singleton Nornir instance that persists across the application
    lifecycle. This prevents multiple initialization overhead and ensures
    consistent state when multiple tools access the Nornir framework.

    The function uses environment variables to locate inventory files:
    - NORNIR_INVENTORY_PATH: Base path for inventory configuration files

    Returns:
        nornir.core.Nornir: A configured Nornir instance with SimpleInventory
            plugin and threaded runner.

    Raises:
        nornir.core.exceptions.NornirNoValidInventoryError: If inventory
            files are missing or invalid.
    """
    global _nr_instance
    if _nr_instance is None:
        _nr_instance = InitNornir(
            inventory={
                "plugin": "SimpleInventory",
                "options": {
                    "host_file": os.path.expandvars(
                        "${NORNIR_INVENTORY_PATH}/hosts.yaml"
                    ),
                    "group_file": os.path.expandvars(
                        "${NORNIR_INVENTORY_PATH}/groups.yaml"
                    ),
                    "defaults_file": os.path.expandvars(
                        "${NORNIR_INVENTORY_PATH}/defaults.yaml"
                    ),
                },
            },
            runner={
                "plugin": "threaded",
            },
        )
    return _nr_instance
