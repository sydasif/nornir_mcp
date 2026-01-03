# Nornir MCP Server

MCP (Model Context Protocol) server for Nornir network automation, enabling LLMs to interact with network devices through standardized tools.

## Overview

This project provides an MCP server that exposes Nornir network automation capabilities to LLMs. It allows AI models to query network device information and perform network operations through a standardized interface.

## Features

- **Host Listing**: Retrieve information about all configured network hosts
- **Device Facts**: Gather comprehensive device information (model, serial, OS version, vendor) using NAPALM
- **Targeted Queries**: Query specific devices or all devices in the inventory
- **Network Automation**: Provides programmatic access to network infrastructure
- **Environment Variable Configuration**: Uses environment variables for inventory path configuration

## Architecture

The server uses:

- **FastMCP**: For MCP protocol implementation
- **Nornir**: For network automation framework
- **NAPALM**: For device interaction and fact gathering
- **Containerlab**: For network device simulation (in development environment)

## Installation

1. Ensure you have Python 3.11+ installed
2. Install `uv` package manager if not already installed:
   ```bash
   pip install uv
   ```
3. Clone the repository and navigate to the project directory
4. Install dependencies using uv:
   ```bash
   uv sync
   ```
5. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Tools

### `list_all_hosts()`

Lists all hosts defined in the Nornir inventory with their names, IP addresses, and platforms.

**Example usage:**
```
list_all_hosts()
```

**Returns:**
- A formatted string containing host names, IPs, and platforms

### `get_device_facts(target_host: str = None)`

Gathers device facts from network equipment using NAPALM. Can target a specific device or retrieve facts from all available devices.

**Parameters:**
- `target_host` (str, optional): Specific hostname to query. If None, queries all hosts in the inventory.

**Example usage:**
```
get_device_facts()              # Get facts for all devices
get_device_facts(target_host="R1")  # Get facts for specific device
```

**Returns:**
- A formatted string containing device facts including model, serial number, OS version, vendor, uptime, and interface list

## Configuration

The server uses programmatic configuration with environment variable expansion:

- **Environment Variable**: `NORNIR_INVENTORY_PATH` - Defines the base path for inventory files
- **Inventory Files** (located at `${NORNIR_INVENTORY_PATH}/`):
  - `hosts.yaml`: Network device definitions
  - `groups.yaml`: Device group configurations
  - `defaults.yaml`: Default configuration values

Configuration is initialized programmatically in the code rather than from external config files.

### Environment Variable Configuration

The `NORNIR_INVENTORY_PATH` environment variable is set in the `.mcp.json` configuration file:

```json
{
    "env": {
        "NORNIR_INVENTORY_PATH": "/opt/inventory"
    }
}
```

## Security Considerations

- Device credentials are managed through Nornir inventory configuration
- Network connectivity requirements must be satisfied for fact gathering
- Device access permissions must be properly configured
- Environment variables should be securely managed in production environments
- Use secure protocols (SSH/HTTPS) for device communication
- Regularly rotate device credentials

## Usage

### Running the Server

The server can be started with:

```bash
uv run python main.py
```

### Connecting to the Server

The server runs as an MCP service and can be connected to by LLM clients that support the MCP protocol. Once connected, the client can invoke the available tools to interact with network devices.

### Example MCP Client Interaction

1. Connect to the MCP server
2. Discover available tools (`list_all_hosts`, `get_device_facts`)
3. Execute tools with appropriate parameters
4. Process the returned results

## Development

The project includes a containerlab environment for testing with simulated network devices (router and switch). The server can be run with `uv run python main.py` and connects to inventory files specified by the `NORNIR_INVENTORY_PATH` environment variable.

### Testing

To test the tools, you can run the server and connect with an MCP-compatible client. The server has been tested with the following tools:
- `list_all_hosts()`: Successfully returns all configured hosts
- `get_device_facts()`: Successfully retrieves device information for all or specific devices

### Project Structure

- `main.py`: Main server implementation with tool definitions
- `.mcp.json`: MCP server configuration including environment variables
- `pyproject.toml`: Project dependencies and metadata
- `README.md`: Project documentation

## Dependencies

- `fastmcp>=2.14.2`: MCP protocol implementation
- `nornir>=3.5.0`: Network automation framework
- `nornir-napalm>=0.5.0`: NAPALM integration for device interaction
- `nornir-utils>=0.2.0`: Utility functions for Nornir
