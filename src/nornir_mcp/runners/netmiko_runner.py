"""Netmiko runner module for Nornir MCP.

This module defines the NetmikoRunner class, which handles execution
of commands using the Netmiko backend.
"""

from typing import Any

from nornir_netmiko.tasks import netmiko_send_command

from ..constants import ErrorType
from ..result import Result
from .base_runner import BaseRunner


class NetmikoRunner(BaseRunner):
    """Runner for Netmiko automation backend.

    Handles execution of raw CLI commands against network devices
    using the Netmiko library.
    """

    def execute(self, **kwargs: Any) -> Result[dict[str, Any], str]:
        """Execute Netmiko command operation.

        Args:
            **kwargs: Must include 'command_string' key with the command to execute,
                     and optional 'host_name' and 'group_name' for filtering

        Returns:
            Result containing either command results or error information
        """
        command_text = kwargs.get("command_string")
        host_name = kwargs.get("host_name")
        group_name = kwargs.get("group_name")

        if not command_text:
            return self.format_error(ErrorType.INVALID_PARAMETERS, "Command string parameter is required")

        # Extract additional kwargs for the Netmiko task
        netmiko_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["command_string", "host_name", "group_name"]
        }

        try:
            aggregated_result = self.run_on_hosts(
                task=netmiko_send_command,
                host_name=host_name,
                group_name=group_name,
                command_string=command_text,
                **netmiko_kwargs,
            )

            return self.process_results(aggregated_result)

        except Exception as error:
            return self.format_error(ErrorType.EXECUTION_ERROR, str(error))

    def run_command(
        self,
        command_string: str,
        host_name: str | None = None,
        group_name: str | None = None,
        **kwargs: Any,
    ) -> Result[dict[str, Any], str]:
        """Execute a CLI command on target hosts.

        Args:
            command_string: The command to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts
            **kwargs: Additional arguments to pass to the Nornir task

        Returns:
            Result containing command results or error information
        """
        all_kwargs = {"command_string": command_string, "host_name": host_name, "group_name": group_name}
        all_kwargs.update(kwargs)
        return self.execute(**all_kwargs)
