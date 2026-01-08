# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nornir MCP Server is a Model Context Protocol (MCP) server that bridges the gap between Large Language Models (LLMs) and network automation. It leverages Nornir, NAPALM, and Netmiko to allow AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Architecture

The project follows a scalable, object-oriented design with explicit separation of concerns:

- **FastMCP**: Handles the Model Context Protocol communication.
- **Nornir Manager**: A singleton (`NornirManager`) that manages the Nornir lifecycle and inventory with thread-safe access.
- **Runners**: Modular execution layer for backend-specific tasks (e.g., `NapalmRunner`, `NetmikoRunner`) that inherit from `BaseRunner`.
- **Result Type**: Custom `Success`/`Error` result wrapper for explicit error handling paths.
- **Constants**: Centralized constants and enumerations for consistent error types, backends, and configuration keys.
- **Utils**: Shared utility functions for target formatting, parameter validation, and data extraction.
- **Types**: Standardized type definitions and error response schemas.
- **Nornir**: Manages inventory, concurrency, and device connections.

### Core Components

- `src/nornir_mcp/main.py`: Entry point that registers tools and resources with the MCP server.
- `src/nornir_mcp/tools.py`: Tool definitions that delegate execution to specific runners.
- `src/nornir_mcp/nornir_init.py`: Singleton manager for Nornir initialization with thread-safe locking.
- `src/nornir_mcp/runners/base_runner.py`: Abstract parent class for all automation runners.
- `src/nornir_mcp/runners/napalm_runner.py`: NAPALM-specific task implementation.
- `src/nornir_mcp/runners/netmiko_runner.py`: Netmiko-specific task implementation.
- `src/nornir_mcp/resources.py`: Provides data-centric resources for LLMs to inspect capabilities.
- `src/nornir_mcp/result.py`: Result type implementation with Success/Error pattern.

## Available Tools

The server exposes the following tools to LLMs:

### Host Management
- **`list_nornir_inventory()`**: Lists all configured network hosts in the inventory.
- **`reload_nornir_inventory()`**: Reloads the Nornir inventory from disk.

### Device Interaction
- **`run_napalm_getter(getter: str, host_name: str | None = None, group_name: str | None = None)`**: Runs a NAPALM getter (e.g., facts, interfaces) on target devices.
- **`run_netmiko_command(command: str, host_name: str | None = None, group_name: str | None = None)`**: Runs a raw CLI command on target devices using Netmiko.
- **`run_paramiko_command(command: str, host_name: str | None = None, group_name: str | None = None, timeout: int = 30)`**: Executes an SSH command on target Linux servers using Paramiko.
- **`paramiko_sftp_upload(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**: Uploads a file to target Linux servers via SFTP using Paramiko.
- **`paramiko_sftp_download(remote_path: str, local_path: str, host_name: str | None = None, group_name: str | None = None)`**: Downloads a file from target Linux servers via SFTP using Paramiko.
- **`paramiko_sftp_list(remote_path: str = ".", host_name: str | None = None, group_name: str | None = None)`**: Lists files and directories in a remote path on target Linux servers via SFTP using Paramiko.
- **`paramiko_scp_upload(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**: Uploads a file to target Linux servers via SCP using Paramiko.
- **`paramiko_scp_download(remote_path: str, local_path: str, host_name: str | None = None, group_name: str | None = None)`**: Downloads a file from target Linux servers via SCP using Paramiko.
- **`paramiko_scp_upload_recursive(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**: Uploads a directory to target Linux servers via SCP using Paramiko recursively.

## Resources

- **`nornir://napalm_getters`**: Returns the list of valid NAPALM getters supported by the server.
- **`nornir://netmiko_commands`**: Returns the list of common Netmiko CLI commands and their descriptions.

## Configuration

The server requires a standard Nornir `config.yaml` file and locates it via:
1. Environment variable: `NORNIR_CONFIG_FILE`
2. Local file: `config.yaml` in the current working directory.

## Development Commands

### Setup and Management
```bash
# Install dependencies
uv sync

# Install in development mode
uv build
uv install -e .

# Run the application
uv run nornir-mcp
```

### Testing
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_tools.py

# Run a specific test
uv run pytest tests/test_tools.py -k "test_run_napalm_getter_success"
```

### Code Quality
```bash
# Lint and Format
uv run ruff check . --fix
uv run ruff format .

# Type Check (if available)
uv run pyright
```

## Key Patterns

- **Singleton Pattern**: `NornirManager.instance()` ensures only one Nornir instance exists with thread-safe access.
- **Runner Pattern**: Backend-specific logic is encapsulated in runner classes inheriting from `BaseRunner` (e.g., `NapalmRunner`, `NetmikoRunner`, `ParamikoRunner`).
- **Result Pattern**: All operations return `Result` type (Success/Error) for explicit error handling.
- **Constants Pattern**: All error types, backends, and configuration keys are defined as enums in `constants.py`.
- **Explicit Type Hints**: All tool functions have explicit return type hints (e.g., `-> dict[str, Any]`) for better MCP schema generation.
- **Read-Only by Default**: `run_napalm_getter` is read-only. `run_netmiko_command` and `run_paramiko_command` can be used for configuration changes.

## Error Handling

The system uses a Result pattern with Success/Error types for explicit error handling. All errors are categorized using `ErrorType` constants for consistent error responses to LLMs.