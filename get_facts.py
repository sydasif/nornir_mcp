from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result


def main():
    # By default, it looks for 'config.yaml' in the current directory
    nr = InitNornir(config_file="config.yaml")

    # We target 'napalm_get' and ask specifically for 'facts'
    result = nr.run(task=napalm_get, getters=["facts"])

    # Print the result in a readable format
    print_result(result)

    # This demonstrates how to access the raw dictionary if you want to process it
    for host, task_result in result.items():
        if not task_result.failed:
            print(f"\nHost: {host}")
            # task_result.result is a dictionary containing the data
            facts = task_result.result["facts"]
            print(f"  Model: {facts['model']}")
            print(f"  Serial: {facts['serial_number']}")
            print(f"  OS Version: {facts['os_version']}")
        else:
            print(f"Failed to connect to {host}")


if __name__ == "__main__":
    main()
