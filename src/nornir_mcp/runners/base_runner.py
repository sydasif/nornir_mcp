"""Base runner module for Nornir MCP.

This module defines the base class for all network automation runners,
providing common functionality and interface for device interaction.
"""

from collections.abc import Callable
from typing import Any

from nornir.core import Nornir
from nornir.core.filter import F
from nornir.core.task import AggregatedResult, MultiResult

from ..constants import ErrorType
from ..types import MCPException


class BaseRunner:
    """Abstract base class for network automation runners.

    Provides common functionality for filtering hosts and formatting
    standardized error responses.
    """

    def __init__(self, nornir: Nornir):
        """Initialize the base runner with a Nornir instance.

        Args:
            nornir: The Nornir instance to use for Nornir operations
        """
        self.nornir = nornir

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
        nr = self.nornir
        if host_name:
            nr = nr.filter(name=host_name)
        elif group_name:
            nr = nr.filter(F(groups__contains=group_name))
        return nr.run(task=task, **kwargs)

    def process_results(
        self, aggregated_result: AggregatedResult, extractor: Callable[[Any], Any] | None = None
    ) -> dict[str, Any]:
        """Process Nornir AggregatedResult into a standardized format.

        Args:
            aggregated_result: The AggregatedResult from Nornir
            extractor: Optional function to extract specific data from the result

        Returns:
            Dictionary containing processed results

        Raises:
            MCPException: If no hosts are found for the given target
        """
        if not aggregated_result:
            raise MCPException(ErrorType.NO_HOSTS, "No hosts found for the given target.")

        processed_data = {}
        for hostname, multi_result in aggregated_result.items():
            # Check if multi_result is empty to avoid IndexError
            if len(multi_result) == 0:
                # For individual host failures, we still return success at the aggregate level
                # but include the error in the data for that specific host
                processed_data[hostname] = {
                    "error": ErrorType.EXECUTION_FAILED,
                    "message": "No task results available for this host",
                }
                continue

            # Check if the multi_result is a MultiResult object with a failed attribute
            # Otherwise, fall back to checking the first item's failed status
            is_multi_result_failed = (
                multi_result.failed
                if isinstance(multi_result, MultiResult)
                else (len(multi_result) > 0 and multi_result[0].failed)
            )

            if is_multi_result_failed:
                # Find the actual task that failed
                failed_task = next((r for r in multi_result if hasattr(r, "failed") and r.failed), None)
                error_message = str(failed_task.exception) if failed_task else "Unknown execution failure"

                processed_data[hostname] = {
                    "error": ErrorType.EXECUTION_FAILED,
                    "message": error_message,
                }
            else:
                # Operation succeeded, safe to grab the first result
                task_output = multi_result[0].result
                if extractor:
                    processed_data[hostname] = extractor(task_output)
                else:
                    processed_data[hostname] = task_output

        return processed_data

    def raise_error(self, error_type: ErrorType | str, message: str) -> None:
        """Raise a standardized error.

        Args:
            error_type: Error type enum or string identifier
            message: Human-readable error message

        Raises:
            MCPException: With the specified error type and message
        """
        # Convert to string (works with StrEnum, str, or other types)
        error_type_str = str(error_type)
        raise MCPException(error_type_str, message)
