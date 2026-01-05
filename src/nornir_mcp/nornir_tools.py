from nornir_napalm.plugins.tasks import napalm_get

from .nornir_init import init_nornir


def list_all_hosts():
    """Retrieve all hosts from the Nornir inventory and return their basic information.

    This function initializes Nornir and iterates through all hosts in the inventory,
    collecting their names, IP addresses, and platform information into a structured
    dictionary format.

    Returns:
        dict: A dictionary containing hosts information with the following structure:
            {
                "hosts": {
                    "hostname1": {
                        "name": "hostname1",
                        "ip": "ip_address",
                        "platform": "platform_name"
                    },
                    ...
                }
            }
            If no hosts are found, returns {"hosts": {}}
            If an error occurs, returns {"error": "inventory_error", "message": str(e)}
    """
    try:
        nr = init_nornir()

        if not nr.inventory.hosts:
            return {"hosts": {}}

        hosts = {}
        for host in nr.inventory.hosts.values():
            hosts[host.name] = {
                "name": host.name,
                "ip": host.hostname,
                "platform": host.platform,
            }

        return {"hosts": hosts}

    except Exception as e:
        return {
            "error": "inventory_error",
            "message": str(e),
        }


def get_device_facts(target_host: str | None = None):
    """Retrieve NAPALM facts for one or all devices in the Nornir inventory.

    This function gathers detailed device information (such as model, serial number,
    operating system version, vendor, etc.) using NAPALM from either a specific host
    or all hosts in the inventory if no target is specified.

    Args:
        target_host (str | None, optional): The name of a specific host to get facts for.
            If None, facts will be retrieved for all hosts in the inventory.
            Defaults to None.

    Returns:
        dict: A dictionary containing the target and facts information with the following structure:
            {
                "target": "hostname or 'all'",
                "facts": {
                    "hostname1": {
                        # NAPALM facts dictionary
                    },
                    ...
                }
            }
            If no hosts are found, returns {"error": "no_hosts", "message": error_message}
            If NAPALM operation fails, returns {"error": "napalm_failed", "message": str(exception)}
            If an execution error occurs, returns {"error": "execution_error", "message": str(e)}
    """
    try:
        nr = init_nornir()

        if target_host:
            nr = nr.filter(name=target_host)

        if not nr.inventory.hosts:
            return {
                "error": "no_hosts",
                "message": f"No hosts found for target: {target_host}",
            }

        result = nr.run(task=napalm_get, getters=["facts"])

        facts = {}
        for host, task_result in result.items():
            if task_result.failed:
                facts[host] = {
                    "error": "napalm_failed",
                    "message": str(task_result.exception),
                }
            else:
                facts[host] = task_result.result.get("facts", {})

        return {
            "target": target_host or "all",
            "facts": facts,
        }

    except Exception as e:
        return {
            "error": "execution_error",
            "message": str(e),
        }
