# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nornir MCP Server is a Model Context Protocol (MCP) server that bridges the gap between Large Language Models (LLMs) and network automation. It leverages Nornir and NAPALM to allow AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Architecture

The project follows a modular design with these key components:

- **FastMCP**: Handles the Model Context Protocol communication
- **Nornir**: Manages inventory, concurrency, and device connections
- **NAPALM**: Provides a unified driver layer to interact with various network operating systems

### Core Files
- `src/nornir_mcp/main.py`: Entry point that registers tools and resources with the MCP server
- `src/nornir_mcp/tools.py`: Contains the core tool definitions (`list_all_hosts` and `get_device_data`)
- `src/nornir_mcp/nornir_init.py`: Handles Nornir initialization with caching using `@lru_cache`
- `src/nornir_mcp/constants.py`: Defines allowed NAPALM getters
- `src/nornir_mcp/resources.py`: Provides resource endpoints for MCP

## Available Tools

### 1. `list_all_hosts`
Retrieves a summary of the entire Nornir inventory, including hostnames, IP addresses, and platform types.

### 2. `get_device_data`
Collects detailed operational data from devices using NAPALM getters:
- `facts`: Basic device information
- `interfaces`: Interface state and speed
- `interfaces_ip`: IP addressing per interface
- `arp_table`: ARP entries
- `mac_address_table`: MAC address table

## Configuration

The server requires a standard Nornir `config.yaml` file and locates it via:
1. Environment variable: `NORNIR_CONFIG_FILE` (absolute path)
2. Local file: `config.yaml` in the current working directory

## Development Commands

### Setup and Management
```bash
# Install dependencies using uv (recommended)
uv sync

# Install in development mode
uv build
uv install -e .

# Run the application
uv run nornir-mcp
```

### Code Quality
```bash
# Lint with Ruff
uv run ruff check .
uv run ruff check . --fix

# Format with Ruff
uv run ruff format .

# Run any tests (if present)
uv run pytest
```

### Python Version
- The project uses Python 3.11 (as specified in `.python-version`)
- Dependencies are managed with `uv` as per `pyproject.toml`

## Key Patterns

- Uses `@lru_cache(maxsize=1)` for singleton Nornir initialization in `nornir_init.py`
- Implements error handling with specific error types in tool functions
- Validates input parameters and returns structured error responses
- Follows a read-only design approach to prevent accidental configuration changes