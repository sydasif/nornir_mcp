# Nornir MCP Server

A **Model Context Protocol (MCP)** server that bridges the gap between Large Language Models (LLMs) and network automation. By leveraging **Nornir** and **NAPALM**, this server allows AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Key Features

* **Inventory Awareness**: Instantly list and filter configured network hosts.
* **Deep Device Insights**: Fetch comprehensive data (facts, interfaces, ARP tables, IP configurations) using unified NAPALM getters.
* **Flexible Targeting**: execute queries against a single specific device or the entire network fleet.
* **Standardized Config**: Built to work with your existing Nornir configuration and inventory files.

## Architecture

The project follows a modular design to ensure reliability and ease of use:

* **FastMCP**: Handles the Model Context Protocol communication.
* **Nornir**: Manages inventory, concurrency, and device connections.
* **NAPALM**: Provides a unified driver layer to interact with various network operating systems.

## Installation

You can install the server globally directly from the repository using `uv` or `pip`:

```bash
# Using uv (Recommended)
uv tool install git+https://github.com/sydasif/nornir_mcp.git

# Using pip
pip install git+https://github.com/sydasif/nornir_mcp.git
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
    "nornir-tool": {
      "command": "nornir-mcp",
      "env": {
        "NORNIR_CONFIG_FILE": "/absolute/path/to/your/config.yaml"
      }
    }
  }
}
```

## Available Tools

The server exposes three primary capabilities to the LLM:

### 1. `list_all_hosts`

Retrieves a summary of the entire Nornir inventory, including hostnames, IP addresses, and platform types.

* **Usage**: `list_all_hosts()`

### 2. `get_device_data`

Collects detailed operational data from devices.

* **Parameters**:
  * `target_host` (optional): The specific device name to query. If omitted, queries all hosts.
  * `getters` (optional): A list of data points to fetch. Defaults to `["facts"]`.
* **Supported Getters**: `facts`, `interfaces`, `interfaces_ip`, `arp_table`, `mac_address_table`.

**Example Prompts**:
> "Get the ARP table and interface IPs for Switch1."
> "Show me basic facts for all routers in the inventory."

### 3. `reload_nornir_inventory`

Reloads the Nornir inventory from disk without restarting the server.

* **Usage**: `reload_nornir_inventory()`
* **Use Case**: Call this after editing your inventory files (hosts.yaml, groups.yaml, defaults.yaml) to refresh the device list and configurations.

**Example Prompt**:
> "I've updated my hosts.yaml file. Please reload the inventory."

## Security & Testing

* **Read-Only Design**: The tools are currently scoped to data retrieval (Getters) to prevent accidental configuration changes.
* **Credentials**: Ensure your Nornir inventory files (`defaults.yaml` or `groups.yaml`) are secured with appropriate file permissions.
* **Lab Environment**: To test safely, you can deploy the container lab provided in the [nornir-mcp-lab repository](https://github.com/sydasif/nornir-mcp-lab.git).

## License

This project is licensed under the MIT License.
