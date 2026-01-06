import os
from typing import Optional

from nornir import InitNornir
from nornir.core import Nornir


class NornirManager:

    _instance: Optional["NornirManager"] = None

    def __init__(self) -> None:
        if NornirManager._instance is not None:
            raise RuntimeError(
                "Use NornirManager.instance() to get the singleton instance."
            )

        self._nornir: Nornir | None = None
        self._config_file: str = self._find_config()

    @classmethod
    def instance(cls) -> "NornirManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _find_config(self) -> str:
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
        if self._nornir is None:
            try:
                self._nornir = InitNornir(config_file=self._config_file)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize Nornir from {self._config_file}: {e}"
                ) from e
        return self._nornir

    def reload(self) -> None:
        self._nornir = None
        self.get()


nornir_manager = NornirManager.instance()
