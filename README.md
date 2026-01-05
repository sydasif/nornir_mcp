# Nornir MCP Server

MCP (Model Context Protocol) server for Nornir network automation, enabling LLMs to interact with network devices through standardized tools.

## Overview

This project provides an MCP server that exposes Nornir network automation capabilities to LLMs. It allows AI models to query network device information and perform network operations through a standardized interface.

## Features

- **Host Listing**: Retrieve information about all configured network hosts
- **Device Data Collection**: Gather comprehensive device information (facts, interfaces, environment, etc.) using NAPALM
- **Targeted Queries**: Query specific devices or all devices in the inventory
- **Network Automation**: Provides programmatic access to network infrastructure
- **Environment Variable Configuration**: Uses environment variables for inventory path configuration

## Architecture

The server follows a modular architecture:

- **FastMCP**: Implementation of the Model Context Protocol using manual tool registration for better control and testability.
- **Nornir**: Network automation framework managing device connections and inventory.
- **NAPALM**: Driver layer for unifying interactions with different network operating systems.

### Code Structure

- `main.py`: Entry point that initializes the server and explicitly registers tools and resources.
- `tools.py`: Pure Python functions implementing the automation logic (independent of the MCP framework).
- `resources.py`: Pure Python functions defining data resources.
- `nornir_init.py`: Thread-safe singleton initialization of the Nornir instance.

## Installation

### Global Installation from GitHub

To install the Nornir MCP server globally from GitHub:

```bash
# Install directly from GitHub repository
uv tool install git+https://github.com/sydasif/nornir_mcp.git

# Or using pip
pip install git+https://github.com/sydasif/nornir_mcp.git
```

Replace `username/nornir-mcp.git` with the actual GitHub repository URL.

## Tools

### `list_all_hosts()`

Lists all hosts defined in the Nornir inventory with their names, IP addresses, and platforms.

**Example usage:**

```bash
list_all_hosts()
```

**Returns:**

- A formatted string containing host names, IPs, and platforms

### `get_device_data(target_host: str = None, getters: list[str] = None)`

Gathers device data from network equipment using NAPALM. Can target a specific device and specify which data points to collect.

**Parameters:**

- `target_host` (str, optional): Specific hostname to query. If None, queries all hosts in the inventory.
- `getters` (list[str] | str, optional): List of NAPALM getters to run or a JSON string representation of the list. Defaults to `["facts"]`.
  - Supported getters: `facts`, `interfaces`, `interfaces_ip`, `arp_table`, `mac_address_table`

**Example usage:**

```bash
get_device_data()                                     # Get basic facts for all devices
get_device_data(target_host="R1")                     # Get basic facts for R1
get_device_data(target_host="R1", getters=["interfaces"]) # Get interface data for R1
```

**Returns:**

- A dictionary containing the query results per device.

## Usage

### Connecting to the Server

The server runs as an MCP service and can be connected to by LLM clients that support the MCP protocol.

```bash
# After installation, add the tool to your MCP server:
claude mcp add nornir-tool --scope <user|local|project> -- nornir-mcp
```

Once connected, the client can invoke the available tools to interact with network devices.

### Configuration

The server uses programmatic configuration with environment variable expansion:

- **Environment Variable**: `NORNIR_INVENTORY_PATH` - Defines the base path for inventory files
- **Inventory Files** (located at `${NORNIR_INVENTORY_PATH}/`):
  - `hosts.yaml`: Network device definitions
  - `groups.yaml`: Device group configurations
  - `defaults.yaml`: Default configuration values

Configuration is initialized programmatically in the code rather than from external config files.

### Environment Variable Configuration

Set the `NORNIR_INVENTORY_PATH` environment variable in configuration file as follows:

```json
{
    "env": {
        "NORNIR_INVENTORY_PATH": "/path/to/inventory"
    }
}
```

> Where are MCP servers stored?
>
> - User and local scope: ~/.claude.json (in the mcpServers field or under project paths)
> - Project scope: .mcp.json in your project root (checked into source control)

### Testing

To test the tools, you can run the server and connect with an MCP-compatible client. The server has been tested with the following tools:

- `list_all_hosts()`: Successfully returns all configured hosts
- `get_device_data()`: Successfully retrieves device information for all or specific devices

## Security Considerations

- Device credentials are managed through Nornir inventory configuration
- Network connectivity requirements must be satisfied for fact gathering
- Device access permissions must be properly configured
- Environment variables should be securely managed in production environments
- Use secure protocols (SSH/HTTPS) for device communication
- Regularly rotate device credentials

## License

This project is licensed under the MIT License.
