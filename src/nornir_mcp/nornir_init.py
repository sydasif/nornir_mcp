"""Nornir initialization module for Model Context Protocol (MCP) server.

This module handles the initialization of the Nornir framework with caching
for performance. The inventory can be explicitly reloaded using the
reload_inventory tool.
"""

import os
from functools import lru_cache

from nornir import InitNornir
from nornir.core import Nornir


@lru_cache(maxsize=1)
def get_nornir(config_file: str | None = None) -> Nornir:
    """Initialize and return a cached Nornir singleton instance.

    This function caches the Nornir instance for performance. The cache
    can be cleared using the reload_inventory() function to refresh
    the inventory from disk.

    Args:
        config_file (str | None): Path to Nornir config file. If None,
            checks NORNIR_CONFIG_FILE env var or looks for config.yaml
            in the current directory.

    Returns:
        Nornir: A cached Nornir instance.

    Raises:
        FileNotFoundError: If no configuration file is found.
        RuntimeError: If Nornir initialization fails.
    """
    try:
        cfg_path = config_file or os.getenv("NORNIR_CONFIG_FILE")

        if not cfg_path:
            default_cfg = "config.yaml"
            if os.path.exists(default_cfg):
                cfg_path = default_cfg

        if not cfg_path:
            raise FileNotFoundError(
                "Nornir configuration file not found. Please set NORNIR_CONFIG_FILE "
                "environment variable or provide a config.yaml in the current directory."
            )

        if not os.path.exists(cfg_path):
            raise FileNotFoundError(
                f"Nornir configuration file not found at: {cfg_path}"
            )

        return InitNornir(config_file=cfg_path)

    except Exception as e:
        raise RuntimeError(f"Failed to initialize Nornir: {e}") from e


def reload_inventory() -> None:
    """Clear the Nornir cache to force reloading from disk.

    This function clears the cached Nornir instance, forcing the next
    call to get_nornir() to re-read and re-parse all configuration and
    inventory files from disk.

    Use this after making changes to your inventory files (hosts.yaml,
    groups.yaml, defaults.yaml) without restarting the MCP server.
    """
    get_nornir.cache_clear()
