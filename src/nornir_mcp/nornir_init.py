"""Nornir initialization module.

This module handles the initialization of the Nornir framework using a
module-level factory pattern. It is driver-agnostic and manages the Nornir lifecycle.
"""

import os
import threading

from nornir import InitNornir
from nornir.core import Nornir

from .constants import DefaultValue, EnvVar

# Module-level variable to store the Nornir instance
_NORNIR_INSTANCE: Nornir | None = None
# Thread lock for thread-safe initialization
_LOCK = threading.Lock()


def get_nornir() -> Nornir:
    """Return the active Nornir instance, initializing it if necessary.

    Returns:
        The active Nornir instance
    """
    global _NORNIR_INSTANCE

    with _LOCK:
        if _NORNIR_INSTANCE is None:
            config_file = _locate_config_file()
            try:
                _NORNIR_INSTANCE = InitNornir(config_file=config_file)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Nornir from {config_file}: {e}") from e
    return _NORNIR_INSTANCE


def reset_nornir() -> None:
    """Force a reload of the Nornir inventory from disk.

    This clears the current Nornir instance and creates a new one,
    effectively reloading the inventory from the configuration file.
    """
    global _NORNIR_INSTANCE

    config_file = _locate_config_file()
    try:
        with _LOCK:
            _NORNIR_INSTANCE = InitNornir(config_file=config_file)
    except Exception as e:
        raise RuntimeError(f"Failed to reload Nornir: {e}") from e


def _locate_config_file() -> str:
    """Locate the Nornir configuration file.

    First checks the NORNIR_CONFIG_FILE environment variable, then
    looks for a local 'config.yaml' file.

    Returns:
        Path to the Nornir configuration file

    Raises:
        FileNotFoundError: If no configuration file is found
    """
    config_path = os.getenv(EnvVar.NORNIR_CONFIG_FILE.value)

    if not config_path:
        default_config_file = DefaultValue.CONFIG_FILENAME.value
        if os.path.exists(default_config_file):
            config_path = default_config_file

    if not config_path or not os.path.exists(config_path):
        display_path = config_path if config_path else DefaultValue.CONFIG_FILENAME.value
        raise FileNotFoundError(
            f"Nornir configuration file not found. Checked env var {EnvVar.NORNIR_CONFIG_FILE.value} "
            f"and local '{display_path}'."
        )

    return config_path
