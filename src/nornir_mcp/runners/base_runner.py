"""Base runner module for Nornir MCP.

This module defines the base class for all network automation runners,
providing common functionality and interface for device interaction.
"""

from abc import ABC
from collections.abc import Callable
from typing import Any

from nornir.core.filter import F
from nornir.core.task import AggregatedResult

from ..nornir_init import NornirManager
from ..types import MCPError, error_response


class BaseRunner(ABC):
    """Parent class for network automation runners.

    Provides common functionality for filtering hosts and formatting
    standardized error responses across different automation backends.
    """

    def __init__(self, manager: NornirManager):
        """Initialize the base runner with a Nornir manager instance.

        Args:
            manager: The NornirManager instance to use for Nornir access
        """
        self.manager = manager

    def run_on_hosts(
        self,
        task: Callable[..., Any],
        host_name: str | None = None,
        group_name: str | None = None,
        **kwargs: Any,
    ) -> AggregatedResult:
        """Execute a task on target hosts with encapsulated filtering.

        Args:
            task: The Nornir task function to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts
            **kwargs: Additional arguments to pass to the task

        Returns:
            AggregatedResult containing the execution results
        """
        nr = self.manager.get()
        if host_name:
            nr = nr.filter(name=host_name)
        elif group_name:
            nr = nr.filter(F(groups__contains=group_name))
        return nr.run(task=task, **kwargs)

    def process_results(
        self, result: AggregatedResult, extractor: Callable[[Any], Any] | None = None
    ) -> dict[str, Any] | MCPError:
        """Process Nornir AggregatedResult into a standardized format.

        Args:
            result: The AggregatedResult from Nornir
            extractor: Optional function to extract specific data from the result

        Returns:
            Dictionary containing processed results or MCPError
        """
        if not result:
            return self.format_error("no_hosts", "No hosts found for the given target.")

        data = {}
        for host, task_result in result.items():
            # Get the result from the first (and usually only) task in the list
            actual_result = task_result[0]

            if actual_result.failed:
                data[host] = self.format_error("execution_failed", str(actual_result.exception))
            else:
                res = actual_result.result
                if extractor:
                    data[host] = extractor(res)
                else:
                    data[host] = res

        return data

    def format_error(self, error_type: str, message: str) -> MCPError:
        """Standardized error response.

        Args:
            error_type: Type of error that occurred
            message: Error message to include in response

        Returns:
            Dictionary containing standardized error format
        """
        return error_response(error_type, message)
