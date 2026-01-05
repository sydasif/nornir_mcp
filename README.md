# Nornir MCP Server

MCP (Model Context Protocol) server for Nornir network automation, enabling LLMs to interact with network devices through standardized tools.

## Overview

This project provides an MCP server that exposes Nornir network automation capabilities to LLMs. It allows AI models to query network device information and perform network operations through a standardized interface.

## Features

- **Host Listing**: Retrieve information about all configured network hosts
- **Device Data Collection**: Gather comprehensive device information (facts, interfaces, ARP, etc.) using NAPALM
- **Targeted Queries**: Query specific devices or all devices in the inventory
- **Network Automation**: Provides programmatic access to network infrastructure
- **Standardized Configuration**: Uses standard Nornir configuration files for predictable behavior

## Architecture

The server follows a modular architecture:

- **FastMCP**: Implementation of the Model Context Protocol using manual tool registration for better control and testability.
- **Nornir**: Network automation framework managing device connections and inventory.
- **NAPALM**: Driver layer for unifying interactions with different network operating systems.

### Code Structure

- `main.py`: Entry point that initializes the server and explicitly registers tools and resources.
- `tools.py`: Pure Python functions implementing the automation logic.
- `resources.py`: Pure Python functions defining data resources.
- `nornir_init.py`: Thread-safe singleton initialization of the Nornir instance using configuration files.

## Installation

### Global Installation from GitHub

To install the Nornir MCP server globally from GitHub:

```bash
# Install directly from GitHub repository
uv tool install git+https://github.com/sydasif/nornir_mcp.git

# Or using pip
pip install git+https://github.com/sydasif/nornir_mcp.git
```

## Configuration

The server requires a standard Nornir configuration file (`config.yaml`) to initialize. It looks for the configuration in the following order:

1.  **Environment Variable**: `NORNIR_CONFIG_FILE` - Set this to the absolute path of your `config.yaml`.
2.  **Local File**: A file named `config.yaml` in the current working directory where the server is started.

### Claude Desktop Configuration

You can add the server to Claude using the CLI:

```bash
claude mcp add nornir-tool --scope user -- nornir-mcp
```

Or manually add it to your `claude.json` or `.mcp.json` with the `NORNIR_CONFIG_FILE` environment variable:

```json
{
  "mcpServers": {
    "nornir-tool": {
      "command": "nornir-mcp",
      "args": [],
      "env": {
        "NORNIR_CONFIG_FILE": "/absolute/path/to/your/config.yaml"
      }
    }
  }
}
```

### Example Nornir Config (`config.yaml`)

```yaml
---
inventory:
  plugin: SimpleInventory
  options:
    host_file: inventory/hosts.yaml
    group_file: inventory/groups.yaml
    defaults_file: inventory/defaults.yaml
runner:
  plugin: threaded
  options:
    num_workers: 20
```

## Tool Usage

The server exposes two primary tools to the LLM.

### 1. `list_all_hosts`

Lists all hosts defined in the Nornir inventory with their names, IP addresses, and platforms.

**Usage:**

```bash
list_all_hosts()
```

**Returns:**
A list of hosts with summary details.

### 2. `get_device_data`

Gathers detailed data from network devices using NAPALM getters.

**Parameters:**

- `target_host` (str, optional): The name of a specific host to query. If omitted, queries **all** hosts.
- `getters` (list[str] | str, optional): The data to collect. Defaults to `["facts"]`.
  - Can be a list: `["facts", "interfaces"]`
  - Can be a JSON string: `'["facts", "interfaces"]'` (Useful for clients that struggle with array inputs)

**Supported Getters:**

- `facts`: Basic device info (Model, OS, Serial, Uptime)
- `interfaces`: Interface status, speed, MTU, MAC
- `interfaces_ip`: IP addresses configured on interfaces
- `arp_table`: ARP cache entries
- `mac_address_table`: MAC address table entries

**Examples:**

- **Get basic facts for all devices:**

    ```python
    get_device_data()
    ```

- **Get facts for a specific router:**

    ```python
    get_device_data(target_host="R1")
    ```

- **Get interface details and IP addresses:**

    ```python
    get_device_data(target_host="Switch1", getters=["interfaces", "interfaces_ip"])
    ```

- **Using JSON string format for getters:**

    ```python
    get_device_data(getters='["arp_table", "mac_address_table"]')
    ```

## Security Considerations

- **Credentials**: Device credentials are managed through your Nornir inventory (`defaults.yaml` or `groups.yaml`). Ensure these files are secured with appropriate file permissions.
- **Connectivity**: The server requires network access to the target devices (SSH/HTTPS).
- **Read-Only**: The current tools are designed for data retrieval (Getters). No configuration change tools are exposed by default.

## License

This project is licensed under the MIT License.
