"""MCP server for Nornir network automation.

Exposes Nornir tools via the Model Context Protocol.
"""

from fastmcp import FastMCP
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get

# Initialize the FastMCP server
# The name "nornir-mcp" identifies this server to the LLM
mcp = FastMCP("nornir-mcp")

# Global Nornir instance (initialized lazily)
_nr_instance = None


def init_nornir():
    """Initialize or return the existing Nornir instance."""
    global _nr_instance
    if _nr_instance is None:
        _nr_instance = InitNornir(config_file="config.yaml")
    return _nr_instance


@mcp.tool()
def list_hosts() -> str:
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


@mcp.tool()
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


# Main entry point for the server
def main():
    mcp.run()


if __name__ == "__main__":
    main()
