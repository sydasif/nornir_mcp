"""Base runner module for Nornir MCP.

This module defines the base class for all network automation runners,
providing common functionality and interface for device interaction.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from nornir.core.filter import F
from nornir.core.task import AggregatedResult

from ..constants import ErrorType
from ..nornir_init import NornirManager
from ..result import Error, Result, Success


class BaseRunner(ABC):
    """Abstract base class for network automation runners.

    All runners must implement the execute() method which performs
    their backend-specific operations. Provides common functionality
    for filtering hosts and formatting standardized error responses.
    """

    def __init__(self, manager: NornirManager):
        """Initialize the base runner with a Nornir manager instance.

        Args:
            manager: The NornirManager instance to use for Nornir access
        """
        self.manager = manager

    @abstractmethod
    def execute(self, **kwargs: Any) -> Result[dict[str, Any], str]:
        """Execute backend-specific operation.

        Subclasses must implement this method to define their
        primary execution logic.

        Args:
            **kwargs: Backend-specific parameters

        Returns:
            Result containing either execution results or error information
        """
        pass

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
        self, aggregated_result: AggregatedResult, extractor: Callable[[Any], Any] | None = None
    ) -> Result[dict[str, Any], str]:
        """Process Nornir AggregatedResult into a standardized format.

        Args:
            aggregated_result: The AggregatedResult from Nornir
            extractor: Optional function to extract specific data from the result

        Returns:
            Result containing either processed results or error information
        """
        if not aggregated_result:
            return self.format_error(ErrorType.NO_HOSTS, "No hosts found for the given target.")

        processed_data = {}
        for hostname, multi_result in aggregated_result.items():
            # Check if multi_result is empty to avoid IndexError
            if len(multi_result) == 0:
                # For individual host failures, we still return success at the aggregate level
                # but include the error in the data for that specific host
                processed_data[hostname] = {
                    "error": ErrorType.EXECUTION_FAILED.value,
                    "message": "No task results available for this host",
                }
                continue

            # Get the result from the first (and usually only) task in the list
            primary_task = multi_result[0]

            if primary_task.failed:
                # For individual host failures, we still return success at the aggregate level
                # but include the error in the data for that specific host
                processed_data[hostname] = {
                    "error": ErrorType.EXECUTION_FAILED.value,
                    "message": str(primary_task.exception),
                }
            else:
                task_output = primary_task.result
                if extractor:
                    processed_data[hostname] = extractor(task_output)
                else:
                    processed_data[hostname] = task_output

        return Success(processed_data)

    def format_error(self, error_type: ErrorType | str, message: str) -> Result[dict[str, Any], str]:
        """Create a standardized error result.

        Args:
            error_type: Error type enum or string identifier
            message: Human-readable error message

        Returns:
            Error Result with the specified error type and message
        """
        # Convert enum to string if needed
        error_type_str = error_type.value if isinstance(error_type, ErrorType) else error_type
        return Error(error_type_str, message)
