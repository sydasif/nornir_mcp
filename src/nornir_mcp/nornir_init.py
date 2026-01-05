"""Nornir initialization module for Model Context Protocol (MCP) server.

This module handles the initialization of the Nornir framework without caching
to support hot-reloading of inventory files.
"""

import os

from nornir import InitNornir
from nornir.core import Nornir


def get_nornir(config_file: str | None = None) -> Nornir:
    """Initialize and return a Nornir instance.

    This function creates a fresh instance on every call to ensure
    inventory changes are reflected immediately.
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
