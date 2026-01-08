"""Netmiko runner module for Nornir MCP.

This module defines the NetmikoRunner class, which handles execution
of commands using the Netmiko backend.
"""

from typing import Any

from nornir_netmiko.tasks import netmiko_send_command

from ..constants import ErrorType
from .base_runner import BaseRunner


class NetmikoRunner(BaseRunner):
    """Runner for Netmiko automation backend.

    Handles execution of raw CLI commands against network devices
    using the Netmiko library.
    """

    def run_command(
        self,
        command_string: str,
        host_name: str | None = None,
        group_name: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a CLI command on target hosts.

        Args:
            command_string: The command to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts
            **kwargs: Additional arguments to pass to the Nornir task

        Returns:
            Dictionary containing command results

        Raises:
            MCPException: If the operation fails

        """
        if not command_string:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Command string parameter is required")

        try:
            aggregated_result = self.run_on_hosts(
                task=netmiko_send_command,
                host_name=host_name,
                group_name=group_name,
                command_string=command_string,
                **kwargs,
            )

            return self.process_results(aggregated_result)
        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))
