"""Base runner module for Nornir MCP.

This module defines the base class for all network automation runners,
providing common functionality and interface for device interaction.
"""

from collections.abc import Callable
from typing import Any

from nornir.core import Nornir
from nornir.core.task import AggregatedResult

from ..nornir_init import NornirManager
from ..types import MCPError


class BaseRunner:
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

    @property
    def nr(self) -> Nornir:
        """Access the Nornir instance from the manager.

        Returns:
            The active Nornir instance managed by the NornirManager
        """
        return self.manager.get()

    def run_on_hosts(
        self,
        task: Callable[..., Any],
        hostname: str | None = None,
        **kwargs: Any,
    ) -> AggregatedResult:
        """Execute a task on target hosts with encapsulated filtering.

        Args:
            task: The Nornir task function to execute
            hostname: Specific hostname to target, or None for all hosts
            **kwargs: Additional arguments to pass to the task

        Returns:
            AggregatedResult containing the execution results
        """
        nr = self.manager.get()
        if hostname:
            nr = nr.filter(name=hostname)
        return nr.run(task=task, **kwargs)

    def format_error(self, error_type: str, message: str) -> MCPError:
        """Standardized error response.

        Args:
            error_type: Type of error that occurred
            message: Error message to include in response

        Returns:
            Dictionary containing standardized error format
        """
        return {"error": error_type, "message": message}
