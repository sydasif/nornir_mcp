# Nornir MCP Server

A **Model Context Protocol (MCP)** server that bridges the gap between Large Language Models (LLMs) and network automation. By leveraging **Nornir**, **NAPALM**, and **Netmiko**, this server allows AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Key Features

* **Inventory Awareness**: Instantly list and filter configured network hosts.
* **Deep Device Insights**: Fetch comprehensive data (facts, interfaces, ARP tables) using NAPALM getters.
* **Direct Command Execution**: Run any CLI command on devices with Netmiko.
* **Explicit Architecture**: Uses dedicated runners for each backend (NAPALM, Netmiko) for clarity and simplicity.
* **Flexible Targeting**: Execute queries against a single specific device or an entire group.
* **Standardized Config**: Built to work with your existing Nornir configuration and inventory files.

## Architecture

The project follows a scalable, object-oriented design to ensure reliability and future-proofing:

* **FastMCP**: Handles the Model Context Protocol communication.
* **Nornir Manager**: A singleton lifecycle manager that handles Nornir initialization and inventory reloading.
* **Runners**: A modular execution layer where specific backend logic (e.g., `NapalmRunner`, `NetmikoRunner`) is isolated from the core server.
* **Types**: Strict typing and error schemas (`MCPError`) ensure consistent and safe communication with LLMs.
* **Nornir**: Manages inventory, concurrency, and device connections.
* **NAPALM**: Provides a unified driver layer to interact with various network operating systems using getters.
* **Netmiko**: Provides a way to send raw CLI commands to devices.

## Installation

You can install the server globally directly from the repository using `uv`:

```bash
uv tool install git+https://github.com/sydasif/nornir_mcp.git
```

## Configuration

The server requires a standard Nornir `config.yaml` file. It locates this configuration in two ways:

1. **Environment Variable**: `NORNIR_CONFIG_FILE` (absolute path).
2. **Local File**: A `config.yaml` located in the current working directory.

### Integration with Claude Desktop

1. To add this tool to Claude, configure your `~/.claude.json` (user) or `.mcp.json` (project) as follows.
2. Ensure you provide the absolute path to your Nornir config:

```json
{
  "mcpServers": {
    "nornir-stack": {
      "command": "nornir-mcp",
      "env": {
        "NORNIR_CONFIG_FILE": "/absolute/path/to/your/config.yaml"
      }
    }
  }
}
```

## Available Tools

The server exposes a set of simple, direct tools to the LLM:

### Host Management

* **`list_nornir_inventory()`**
  Lists all configured network hosts in the inventory, including hostnames, IP addresses, and platform types.

* **`reload_nornir_inventory()`**
  Reloads the Nornir inventory from disk. Use this after editing your inventory files to apply changes without restarting the server.

### Device Interaction Tools

The server provides dedicated tools for NAPALM getters and Netmiko commands.

* **`run_napalm_getter(getter: str, host_name: str | None = None, group_name: str | None = None)`**
  Executes a specific NAPALM getter on a target device to retrieve structured data.

  **Arguments:**
  * `getter`: The specific data to fetch (e.g., `"facts"`, `"interfaces"`, `"arp_table"`). See `nornir://napalm_capabilities` for a full list.
  * `host_name`: (Optional) The specific device to target. If omitted, runs against all devices.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`run_netmiko_command(command: str, host_name: str | None = None, group_name: str | None = None, **kwargs)`**
  Executes a raw CLI command on a target device using Netmiko.

  **Arguments:**
  * `command`: The exact CLI command to execute (e.g., `"show version"`, `"show ip route"`).
  * `host_name`: (Optional) The specific device to target.
  * `group_name`: (Optional) The specific group to target.
  * `**kwargs`: (Optional) Additional arguments passed directly to the Netmiko task (e.g., `enable=True`, `read_timeout=60`).

**Example Usage:**

```python
# Get basic facts for all devices using NAPALM
run_napalm_getter(getter="facts")

# Get interfaces for a specific switch using NAPALM
run_napalm_getter(getter="interfaces", host_name="switch-01")

# Get the routing table from a specific router using Netmiko
run_netmiko_command(command="show ip route", host_name="router-01")

# Get the running configuration for all devices in the 'core' group
run_netmiko_command(command="show running-config", group_name="core")

# Send a command requiring enable mode with a custom timeout
run_netmiko_command(command="show tech-support", host_name="firewall-01", enable=True, read_timeout=120)
```

### Resources

The server exposes dynamic resources to help discover capabilities:

* **`nornir://napalm_capabilities`**
  Returns a list of all valid getter names supported by the NAPALM runner. This is useful for knowing what can be passed to the `run_napalm_getter` tool.

## Security & Testing

* **Read-Only by Default**: The `run_napalm_getter` tool is read-only. `run_netmiko_command` can execute configuration commands, so use it with caution.
* **Credentials**: Ensure your Nornir inventory files (`defaults.yaml` or `groups.yaml`) are secured with appropriate file permissions.
* **Lab Environment**: To test safely, you can deploy the container lab provided in the [nornir-mcp-lab](https://github.com/sydasif/nornir-mcp-lab.git) repository.

## License

This project is licensed under the MIT License.
