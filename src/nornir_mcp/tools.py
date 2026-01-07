"""Tools module for Nornir MCP server.

This module contains the core tool definitions that are exposed to the MCP
server. It delegates execution to specific Runners (NAPALM, etc) for
performing network automation tasks.
"""

from typing import Any

from .nornir_init import nornir_manager
from .resources import get_inventory
from .runners.napalm_runner import NapalmRunner
from .runners.registry import RunnerRegistry
from .types import MCPError, error_response

_registry: RunnerRegistry | None = None


def get_registry() -> RunnerRegistry:
    """Get the runner registry, initializing it if necessary."""
    global _registry
    if _registry is None:
        _registry = RunnerRegistry()
        _registry.register("napalm", NapalmRunner(nornir_manager))
    return _registry


def run_napalm_getter(
    backend: str, getter: str, host_name: str | None = None, group_name: str | None = None
) -> dict[str, Any] | MCPError:
    """Generic tool to run a getter on a network device.

    Args:
        backend: The automation backend to use (e.g., 'napalm')
        getter: The getter method to execute (e.g., 'facts', 'interfaces')
        host_name: (Optional) Specific host name to target. Omit to target ALL hosts.
        group_name: (Optional) Specific group to target. Cannot be used with host_name.

    Returns:
        Dictionary containing the results of the getter execution
    """
    if host_name and group_name:
        return error_response("invalid_parameters", "Cannot specify both host_name and group_name")

    try:
        registry = get_registry()
        runner = registry.get(backend)
        raw_result = runner.run_getter(getter, host_name, group_name)

        # Check if runner returned an error
        if isinstance(raw_result, dict) and "error" in raw_result:
            return raw_result  # Already formatted as MCPError

        target = host_name or f"group:{group_name}" or "all"
        return {
            "backend": backend,
            "getter": getter,
            "target": target,
            "data": raw_result,
        }
    except KeyError as e:
        return error_response("unknown_backend", str(e).strip("'"))
    except Exception as e:
        return error_response("tool_error", str(e))


def list_nornir_inventory() -> dict[str, Any] | MCPError:
    """List all configured network hosts in the inventory.

    Returns:
        Dictionary containing all hosts or MCPError
    """
    return get_inventory()


def reload_nornir_inventory() -> dict[str, str] | MCPError:
    """Reload Nornir inventory from disk to apply changes.

    Returns:
        Dictionary indicating success or failure of the reload operation
    """
    try:
        nornir_manager.reload()
        return {
            "status": "success",
            "message": "Nornir inventory reloaded from disk.",
        }
    except Exception as e:
        return error_response("reload_failed", str(e))
