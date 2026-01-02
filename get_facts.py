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


if __name__ == "__main__":
    main()
