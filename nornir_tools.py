"""Nornir tools module for Nornir network automation.

This module contains the tool definitions for the Model Context Protocol (MCP) server
that exposes Nornir network automation capabilities to LLMs. It provides standardized
tools for network device discovery, fact gathering, and configuration
management through the MCP interface.

This module is part of the refactored architecture that separates concerns:
- nornir_init.py: Handles Nornir initialization and instance management
- nornir_tools.py: Contains tool definitions

The server exposes the following tools:
- list_all_hosts: Lists all network devices in the Nornir inventory
- get_device_facts: Retrieves detailed device information using NAPALM
"""

from nornir_napalm.plugins.tasks import napalm_get

from nornir_init import init_nornir


def list_all_hosts() -> str:
    """List all hosts defined in the Nornir inventory.

    Returns:
        A formatted string containing host names, IPs, and platforms.
    """
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
    """Gather device facts (model, serial, OS version) using NAPALM.

    Args:
        target_host: Optional specific hostname to query.
                     If None, queries all hosts in the inventory.

    Returns:
        A formatted string containing device facts.
    """
    try:
        nr = init_nornir()

        # Filter inventory if a specific host is requested
        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return f"No hosts found matching criteria: {target_host}"

        # Run the NAPALM task
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
