"""NAPALM runner implementation.

This module provides NAPALM-specific task execution capabilities
for the Nornir MCP server, handling device data retrieval operations.
"""

from typing import Any

from nornir_napalm.plugins.tasks import napalm_get

from ..constants import ErrorType
from .base_runner import BaseRunner


class NapalmRunner(BaseRunner):
    """Runner for NAPALM-specific tasks.

    Handles NAPALM-based network device interactions and data retrieval
    operations through standardized getter methods.
    """

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute NAPALM getter operation.

        Args:
            **kwargs: Must include 'getter' key with the NAPALM getter name,
                     and optional 'host_name' and 'group_name' for filtering

        Returns:
            Dictionary containing getter results

        Raises:
            MCPException: If the operation fails
        """
        getter_name = kwargs.get("getter")
        host_name = kwargs.get("host_name")
        group_name = kwargs.get("group_name")

        if not getter_name:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Getter parameter is required")

        try:
            aggregated_result = self.run_on_hosts(
                task=napalm_get, host_name=host_name, group_name=group_name, getters=[getter_name]
            )

            # Define an extractor to pull only the specific getter data
            def extract_getter_data(task_output: Any) -> Any:
                return task_output.get(getter_name) if isinstance(task_output, dict) else task_output

            return self.process_results(aggregated_result, extractor=extract_getter_data)

        except ValueError as error:
            # NAPALM raises ValueError for invalid getters
            self.raise_error(ErrorType.INVALID_GETTER, str(error))
        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def run_getter(
        self, getter: str, host_name: str | None = None, group_name: str | None = None
    ) -> dict[str, Any]:
        """Execute a specific NAPALM getter against devices.

        Args:
            getter: The NAPALM getter method to execute (e.g., 'facts', 'interfaces')
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing getter results

        Raises:
            MCPException: If the operation fails
        """
        return self.execute(getter=getter, host_name=host_name, group_name=group_name)
