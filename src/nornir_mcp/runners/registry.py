"""Runner registry module for Nornir MCP server.

This module provides a centralized registry for managing different network
automation runners (e.g., NAPALM, Netmiko) that can be dynamically loaded
and accessed by the tools.
"""

from .base_runner import BaseRunner


class RunnerRegistry:
    """Centralized registry for managing network automation runners.

    This class provides a way to register, retrieve, and manage different
    automation backends (e.g., NAPALM, Netmiko) that can be used by the
    MCP server tools to interact with network devices.
    """

    def __init__(self) -> None:
        self._runners: dict[str, BaseRunner] = {}

    def register(self, name: str, runner: BaseRunner) -> None:
        """Register a new automation runner.

        Args:
            name: The name of the backend (e.g., 'napalm')
            runner: The runner instance to register

        Raises:
            ValueError: If a runner with the same name is already registered
        """
        if name in self._runners:
            raise ValueError(f"Runner '{name}' already registered.")
        self._runners[name] = runner

    def get(self, name: str) -> BaseRunner:
        """Retrieve a runner by name.

        Args:
            name: The name of the runner to retrieve

        Returns:
            The registered BaseRunner instance

        Raises:
            KeyError: If no runner is registered with the given name
        """
        if name not in self._runners:
            available = ", ".join(self._runners.keys())
            raise KeyError(f"Backend '{name}' not found. Available backends: {available or 'none'}")
        return self._runners[name]

    def list_runners(self) -> list[str]:
        """List all registered runner names.

        Returns:
            List of backend names
        """
        return list(self._runners.keys())

    def reset(self) -> None:
        """Reset the registry, clearing all registered runners.

        Useful for testing isolation.
        """
        self._runners.clear()
