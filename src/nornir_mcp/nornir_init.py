"""Nornir initialization module.

This module handles the initialization of the Nornir framework using a
Singleton pattern. It is driver-agnostic and manages the Nornir lifecycle.
"""

import os
import threading

from nornir import InitNornir
from nornir.core import Nornir

from .constants import DefaultValue, EnvVar


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

    def _locate_config_file(self) -> str:
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

    def get(self) -> Nornir:
        """Return the active Nornir instance, initializing it if necessary.

        Returns:
            The active Nornir instance
        """
        with self._lock:
            if self._config_file is None:
                self._config_file = self._locate_config_file()

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
            self._config_file = self._locate_config_file()
            try:
                self._nornir = InitNornir(config_file=self._config_file)
            except Exception as e:
                raise RuntimeError(f"Failed to reload Nornir: {e}") from e
