"""Tools module for Nornir MCP server.

This module contains the core tool definitions that are exposed to the MCP
server. It delegates execution to specific Runners (NAPALM, etc) for
performing network automation tasks.
"""

from typing import Any

from .nornir_init import nornir_manager
from .runners.napalm_runner import NapalmRunner
from .runners.registry import RunnerRegistry
from .types import MCPError

napalm_runner = NapalmRunner(nornir_manager)
registry = RunnerRegistry()
registry.register("napalm", napalm_runner)


def list_all_hosts() -> dict[str, Any] | MCPError:
    """List all configured network hosts in the inventory.

    Returns:
        Dictionary containing all hosts with their basic information
        (name, IP address, platform)
    """
    try:
        nr = nornir_manager.get()

        if not nr.inventory.hosts:
            return {"hosts": {}}

        hosts = {
            host.name: {
                "name": host.name,
                "ip": host.hostname,
                "platform": host.platform,
            }
            for host in nr.inventory.hosts.values()
        }

        return {"hosts": hosts}

    except Exception as e:
        return MCPError(error="inventory_error", message=str(e))


def run_getter(
    backend: str, getter: str, hostname: str | None = None
) -> dict[str, Any] | MCPError:
    """Generic tool to run a getter on a network device.

    Args:
        backend: The automation backend to use (e.g., 'napalm')
        getter: The getter method to execute (e.g., 'facts', 'interfaces')
        hostname: (optional) Specific hostname to target, or Omit for all hosts

    Returns:
        Dictionary containing the results of the getter execution
    """
    try:
        runner = registry.get(backend)
        raw_result = runner.run_getter(getter, hostname)

        return {
            "backend": backend,
            "getter": getter,
            "target": hostname or "all",
            "data": raw_result,
        }
    except KeyError:
        return MCPError(
            error="unknown_backend",
            message=f"Backend '{backend}' not found.",
        )
    except Exception as e:
        return MCPError(error="tool_error", message=str(e))


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
        return MCPError(error="reload_failed", message=str(e))
