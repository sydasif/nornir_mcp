"""Nornir initialization module.

This module handles the initialization of the Nornir framework using a
Singleton pattern. It is driver-agnostic and manages the Nornir lifecycle.
"""

import os
import threading

from nornir import InitNornir
from nornir.core import Nornir


class NornirManager:
    """Singleton class to manage the Nornir instance and lifecycle.

    Handles Nornir initialization, configuration file discovery, and
    provides thread-safe access to the Nornir instance across the application.
    """

    _instance: "NornirManager | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize the NornirManager singleton instance.

        Raises:
            RuntimeError: If an instance already exists (enforces singleton pattern)
        """
        if NornirManager._instance is not None:
            raise RuntimeError("Use NornirManager.instance() to get the singleton instance.")

        self._nornir: Nornir | None = None
        self._config_file: str | None = None

    @classmethod
    def instance(cls) -> "NornirManager":
        """Get the singleton instance of NornirManager.

        Returns:
            The singleton NornirManager instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _find_config(self) -> str:
        """Locate the Nornir configuration file.

        First checks the NORNIR_CONFIG_FILE environment variable, then
        looks for a local 'config.yaml' file.

        Returns:
            Path to the Nornir configuration file

        Raises:
            FileNotFoundError: If no configuration file is found
        """
        path = os.getenv("NORNIR_CONFIG_FILE")

        if not path:
            default_cfg = "config.yaml"
            if os.path.exists(default_cfg):
                path = default_cfg

        if not path or not os.path.exists(path):
            display_path = path or "config.yaml"
            raise FileNotFoundError(
                f"Nornir configuration file not found. Checked env var NORNIR_CONFIG_FILE "
                f"and local '{display_path}'."
            )

        return path

    def get(self) -> Nornir:
        """Return the active Nornir instance, initializing it if necessary.

        Returns:
            The active Nornir instance
        """
        with self._lock:
            if self._config_file is None:
                self._config_file = self._find_config()

            if self._nornir is None:
                try:
                    self._nornir = InitNornir(config_file=self._config_file)
                except Exception as e:
                    raise RuntimeError(f"Failed to initialize Nornir from {self._config_file}: {e}") from e
        return self._nornir

    def reload(self) -> None:
        """Force a reload of the Nornir inventory from disk.

        This clears the current Nornir instance and creates a new one,
        effectively reloading the inventory from the configuration file.
        Thread-safe implementation using double-checked locking pattern.
        """
        with self._lock:
            self._config_file = self._find_config()
            try:
                self._nornir = InitNornir(config_file=self._config_file)
            except Exception as e:
                raise RuntimeError(f"Failed to reload Nornir: {e}") from e


