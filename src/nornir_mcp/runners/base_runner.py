"""Base runner module for Nornir MCP.

This module defines the base class for all network automation runners,
providing common functionality and interface for device interaction.
"""

from nornir.core import Nornir

from ..nornir_init import NornirManager


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

    def get_target_hosts(self, hostname: str | None = None) -> Nornir:
        """Filter the Nornir inventory based on hostname.

        Args:
            hostname: Specific hostname to filter for, or None for all hosts

        Returns:
            Nornir instance with filtered inventory
        """
        nr = self.nr
        if hostname:
            nr = nr.filter(name=hostname)
        return nr

    def format_error(self, error_type: str, message: str) -> dict[str, str]:
        """Standardized error response.

        Args:
            error_type: Type of error that occurred
            message: Error message to include in response

        Returns:
            Dictionary containing standardized error format
        """
        return {"error": error_type, "message": message}
