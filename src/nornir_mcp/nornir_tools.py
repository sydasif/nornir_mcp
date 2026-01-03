"""Nornir tools module for Model Context Protocol (MCP) server."""

from nornir_napalm.plugins.tasks import napalm_get

from .nornir_init import init_nornir


def list_all_hosts() -> str:
    """List all hosts in the inventory."""

    try:
        nr = init_nornir()
        output = ["Available Hosts:"]

        if not nr.inventory.hosts:
            return "No hosts found in inventory."

        for host in nr.inventory.hosts.values():
            output.append(
                f"- Name: {host.name}, IP: {host.hostname}, Platform: {host.platform}"
            )
        return "\n".join(output)
    except Exception as e:
        return f"Error listing hosts: {str(e)}"


def get_device_facts(target_host: str = None) -> str:
    """Get device facts for a specific host or all hosts."""
    try:
        nr = init_nornir()

        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return f"No hosts found matching criteria: {target_host}"

        result = nr.run(task=napalm_get, getters=["facts"])

        summary = []
        for host, task_result in result.items():
            if task_result.failed:
                summary.append(f"Host: {host} - FAILED to get facts")
            else:
                # Extract data from NAPALM result
                facts = task_result.result["facts"]
                summary.append(
                    f"Host: {facts['hostname']}\n"
                    f"  - Model: {facts['model']}\n"
                    f"  - Serial: {facts['serial_number']}\n"
                    f"  - OS Version: {facts['os_version']}\n"
                    f"  - Vendor: {facts['vendor']}\n"
                    f"  - Uptime (seconds): {facts['uptime']}\n"
                    f"  - Interfaces: {', '.join(facts['interface_list'])}"
                )

        return "\n".join(summary)

    except Exception as e:
        return f"Error getting facts: {str(e)}"
