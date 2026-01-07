"""Netmiko runner module for Nornir MCP.

This module defines the NetmikoRunner class, which handles execution
of commands using the Netmiko backend.
"""

from typing import Any

from nornir_netmiko.tasks import netmiko_send_command

from ..types import MCPError
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
    ) -> dict[str, Any] | MCPError:
        """Execute a CLI command on target hosts.

        Args:
            command_string: The command to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing command results or MCPError
        """
        try:
            result = self.run_on_hosts(
                task=netmiko_send_command,
                host_name=host_name,
                group_name=group_name,
                command_string=command_string,
            )

            return self.process_results(result)

        except Exception as e:
            return self.format_error("execution_error", str(e))

    def run_getter(
        self, getter: str, host_name: str | None = None, group_name: str | None = None
    ) -> dict[str, Any] | MCPError:
        """Execute a specific getter against devices.

        Netmiko does not support getters in the same way as NAPALM.
        This method is implemented to satisfy the abstract base class
        but returns an error indicating incompatibility.
        """
        return self.format_error("not_supported", "Netmiko runner does not support getters.")
