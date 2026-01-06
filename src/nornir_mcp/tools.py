from typing import Any

from .nornir_init import nornir_manager
from .runners.napalm_runner import NapalmRunner

napalm_runner = NapalmRunner(nornir_manager)


def list_all_hosts() -> dict[str, Any]:
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
        return {"error": "inventory_error", "message": str(e)}


def get_facts(hostname: str | None = None) -> dict[str, Any]:
    return napalm_runner.run_getter("facts", hostname)


def get_interfaces(hostname: str | None = None) -> dict[str, Any]:
    return napalm_runner.run_getter("interfaces", hostname)


def get_interfaces_ip(hostname: str | None = None) -> dict[str, Any]:
    return napalm_runner.run_getter("interfaces_ip", hostname)


def get_arp_table(hostname: str | None = None) -> dict[str, Any]:
    return napalm_runner.run_getter("arp_table", hostname)


def get_mac_address_table(hostname: str | None = None) -> dict[str, Any]:
    return napalm_runner.run_getter("mac_address_table", hostname)


def reload_nornir_inventory() -> dict[str, str]:
    try:
        nornir_manager.reload()
        return {
            "status": "success",
            "message": "Nornir inventory reloaded from disk.",
        }
    except Exception as e:
        return {
            "error": "reload_failed",
            "message": str(e),
        }
