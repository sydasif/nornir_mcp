"""Nornir initialization module for Model Context Protocol (MCP) server."""

import os

from nornir import InitNornir

_nr_instance = None


def init_nornir():
    """Initialize or return the existing Nornir instance using singleton pattern."""
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
