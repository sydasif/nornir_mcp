# CLAUDE.local.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Nornir MCP Server is an implementation of the Model Context Protocol (MCP) that exposes Nornir network automation capabilities to LLMs. It allows AI models to interact with network devices through standardized tools for device discovery, fact gathering, and configuration management.

## Architecture

- **FastMCP**: Provides the Model Context Protocol implementation
- **Nornir**: Network automation framework for managing network device connections
- **NAPALM**: Used for device interaction and fact gathering from network equipment
- **Containerlab**: Used for network device simulation in development environments

## Code Structure

- `main.py`: Main application entry point that contains the MCP server implementation and registers tools
- `nornir_init.py`: Handles Nornir initialization and instance management
- `nornir_tools.py`: Contains tool definitions for network automation
- `.mcp.json`: MCP server configuration including environment variables
- `pyproject.toml`: Project dependencies and metadata
- `README.md`: Project documentation

## MCP Tools

The server exposes these primary tools:

1. `list_all_hosts()`: Lists all network devices in the Nornir inventory with names, IP addresses, and platforms
2. `get_device_facts(target_host: str = None)`: Retrieves detailed device information (model, serial, OS version, vendor, etc.) using NAPALM

## Development Commands

### Environment Setup

```bash
# Using uv for package management
uv sync
uv run python main.py
```

### Linting and Formatting

```bash
uv run ruff check . --fix
uv run ruff format .
```

### Running the Server

```bash
uv run python main.py
```

## Configuration

The server uses programmatic Nornir initialization without external config files, using:

- Environment variable: `NORNIR_INVENTORY_PATH` - Defines the base path for inventory files
- Inventory files (located at `${NORNIR_INVENTORY_PATH}/`):
  - `hosts.yaml`: Network device definitions
  - `groups.yaml`: Device group configurations
  - `defaults.yaml`: Default configuration values

The `NORNIR_INVENTORY_PATH` environment variable is configured in `.mcp.json`:
```json
{
    "env": {
        "NORNIR_INVENTORY_PATH": "/opt/inventory"
    }
}
```

## Development Environment

The project connects to network inventory files specified by the `NORNIR_INVENTORY_PATH` environment variable.

## Security Considerations

- Device credentials are managed through Nornir inventory configuration
- Network connectivity requirements must be satisfied for fact gathering
- Device access permissions must be properly configured
- Environment variables should be securely managed in production environments
