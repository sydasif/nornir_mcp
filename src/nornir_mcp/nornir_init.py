"""Nornir initialization module for Model Context Protocol (MCP) server.

This module handles the initialization of the Nornir framework using
Python's lru_cache to implement the singleton pattern.
"""

import os
from functools import lru_cache

from nornir import InitNornir
from nornir.core import Nornir


@lru_cache(maxsize=1)
def _get_nornir_cached(config_file: str | None = None) -> Nornir:
    """Internal cached function to initialize Nornir."""
    try:
        # Priority 1: Configuration file argument or environment variable
        cfg_path = config_file or os.getenv("NORNIR_CONFIG_FILE")

        # Priority 2: Default config.yaml in current directory
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


def get_nornir(config_file: str | None = None, force_reload: bool = False) -> Nornir:
    """Initialize or return the existing Nornir instance.

    Uses a cached internal function to implement the singleton pattern.
    Requires a Nornir configuration file (YAML).

    Args:
        config_file: Optional path to a Nornir configuration file.
            Overrides NORNIR_CONFIG_FILE env var.
        force_reload: If True, clears the cache and re-initializes Nornir.

    Returns:
        nornir.core.Nornir: A configured Nornir instance.

    Raises:
        RuntimeError: If Nornir initialization fails or config is missing.
    """
    if force_reload:
        _get_nornir_cached.cache_clear()

    return _get_nornir_cached(config_file)
