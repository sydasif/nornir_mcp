"""Nornir initialization module for Nornir MCP server.

This module handles the initialization and management of the Nornir instance
used by the MCP server. It provides a singleton pattern to maintain a single
Nornir instance across the application lifecycle.

This module is part of the refactored architecture that separates concerns:
- nornir_init.py: Handles Nornir initialization and instance management
- mcp_server.py: Contains MCP server implementation and tool definitions
"""

import os

from nornir import InitNornir

# Global Nornir instance to maintain connection across requests
# This singleton pattern ensures we don't reinitialize Nornir on each tool call
_nr_instance = None


def init_nornir():
    """Initialize or return the existing Nornir instance."""
    global _nr_instance
    if _nr_instance is None:
        # Initialize Nornir programmatically without config file
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
