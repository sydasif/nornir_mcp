"""Nornir initialization module for Model Context Protocol (MCP) server.

This module handles the initialization of the Nornir framework using
Python's lru_cache to implement the singleton pattern.
"""

import os
from functools import lru_cache

from nornir import InitNornir
from nornir.core import Nornir


@lru_cache(maxsize=1)
def get_nornir() -> Nornir:
    """Initialize or return the existing Nornir instance.

    Uses functools.lru_cache to implement the singleton pattern, ensuring
    only one Nornir instance is created and reused.

    The function uses environment variables to locate inventory files:
    - NORNIR_INVENTORY_PATH: Base path for inventory configuration files

    Returns:
        nornir.core.Nornir: A configured Nornir instance with SimpleInventory
            plugin and threaded runner.
    """
    return InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": os.path.expandvars("${NORNIR_INVENTORY_PATH}/hosts.yaml"),
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
