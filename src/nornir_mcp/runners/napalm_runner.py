"""NAPALM runner implementation.

This module provides NAPALM-specific task execution capabilities
for the Nornir MCP server, handling device data retrieval operations.
"""

import json
from pathlib import Path
from typing import Any

from nornir_napalm.plugins.tasks import napalm_get

from ..types import MCPError
from .base_runner import BaseRunner


class NapalmRunner(BaseRunner):
    """Runner for NAPALM-specific tasks.

    Handles NAPALM-based network device interactions and data retrieval
    operations through standardized getter methods.
    """

    @property
    def supported_getters(self) -> set[str]:
        """Load and return the set of supported NAPALM getters from JSON configuration."""
        if not hasattr(self, "_supported_getters"):
            try:
                # Navigate from runners/napalm_runner.py to supported_getters.json
                # Structure: src/nornir_mcp/runners/napalm_runner.py -> src/nornir_mcp/supported_getters.json
                json_path = Path(__file__).parent.parent / "supported_getters.json"

                with open(json_path) as f:
                    data = json.load(f)

                # Extract keys from the "supported_getters" dictionary
                self._supported_getters = set(data.get("supported_getters", {}).keys())
            except Exception:
                # Fallback to empty set if file cannot be read
                self._supported_getters = set()

        return self._supported_getters

    def run_getter(
        self, getter: str, hostname: str | None = None
    ) -> dict[str, Any] | MCPError:
        """Execute a specific NAPALM getter against devices.

        Args:
            getter: The NAPALM getter method to execute (e.g., 'facts', 'interfaces')
            hostname: Specific hostname to target, or None for all hosts

        Returns:
            Dictionary containing getter results with standardized format
        """
        if getter not in self.supported_getters:
            return self.format_error(
                "invalid_getter", f"Getter '{getter}' is not supported by NapalmRunner."
            )

        try:
            result = self.run_on_hosts(
                task=napalm_get, hostname=hostname, getters=[getter]
            )

            if not result:
                return self.format_error(
                    "no_hosts", f"No hosts found for target: {hostname or 'all'}"
                )

            data = {}
            for host, task_result in result.items():
                actual_result = task_result[0]

                if actual_result.failed:
                    data[host] = self.format_error(
                        "napalm_failed", str(actual_result.exception)
                    )
                else:
                    res = actual_result.result
                    data[host] = res.get(getter) if isinstance(res, dict) else res

            return data

        except Exception as e:
            return self.format_error("execution_error", str(e))
