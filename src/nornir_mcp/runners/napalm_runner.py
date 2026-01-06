"""NAPALM runner implementation.

This module provides NAPALM-specific task execution capabilities
for the Nornir MCP server, handling device data retrieval operations.
"""

from typing import Any

from nornir_napalm.plugins.tasks import napalm_get

from ..types import MCPError
from .base_runner import BaseRunner


class NapalmRunner(BaseRunner):
    """Runner for NAPALM-specific tasks.

    Handles NAPALM-based network device interactions and data retrieval
    operations through standardized getter methods.
    """

    def run_getter(
        self, getter: str, host_name: str | None = None, group_name: str | None = None
    ) -> dict[str, Any] | MCPError:
        """Execute a specific NAPALM getter against devices.

        Args:
            getter: The NAPALM getter method to execute (e.g., 'facts', 'interfaces')
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing getter results with standardized format
        """
        try:
            result = self.run_on_hosts(
                task=napalm_get, host_name=host_name, group_name=group_name, getters=[getter]
            )

            # Define an extractor to pull only the specific getter data
            def extract_getter(res: Any) -> Any:
                return res.get(getter) if isinstance(res, dict) else res

            return self.process_results(result, extractor=extract_getter)

        except Exception as e:
            return self.format_error("execution_error", str(e))
