# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nornir MCP Server is a Model Context Protocol (MCP) server that bridges the gap between Large Language Models (LLMs) and network automation. It leverages Nornir and NAPALM to allow AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Architecture

The project follows a scalable, object-oriented design:

- **FastMCP**: Handles the Model Context Protocol communication.
- **Nornir Manager**: A singleton (`NornirManager`) that manages the Nornir lifecycle and inventory.
- **Runners**: Modular execution layer for driver-specific tasks (e.g., `NapalmRunner`).
- **Nornir**: Manages inventory, concurrency, and device connections.

### Core Files

- `src/nornir_mcp/main.py`: Entry point that registers tools with the MCP server.
- `src/nornir_mcp/tools.py`: Tool definitions that delegate execution to specific runners.
- `src/nornir_mcp/nornir_init.py`: Singleton manager for Nornir initialization.
- `src/nornir_mcp/runners/base_runner.py`: Parent class for all automation runners.
- `src/nornir_mcp/runners/napalm_runner.py`: NAPALM-specific task implementation.

## Available Tools

The server exposes a set of simple, direct tools to the LLM:

### Host Management

- **`list_all_hosts()`**
  Retrieves a summary of the entire Nornir inventory.

- **`reload_nornir_inventory()`**
  Reloads the Nornir inventory from disk.

### Device Data Getter

- **`run_getter(backend: str, getter: str, hostname: str | None = None)`**
  Generic tool to run a getter (e.g., facts, interfaces) on target devices using a specific backend.

## Resources

- **`nornir://inventory`**
  Returns a summary of the current Nornir inventory (hosts, IPs, platforms).

- **`nornir://capabilities`**
  Returns the list of valid NAPALM getters supported by the server.

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

### Code Quality

```bash
# Lint and Format
uv run ruff check . --fix
uv run ruff format .

# Type Check
uv run pyright
```

## Key Patterns

- **Singleton Pattern**: `NornirManager.instance()` ensures only one Nornir instance exists.
- **Runner Pattern**: Driver-specific logic is encapsulated in runner classes inheriting from `BaseRunner`.
- **Explicit Type Hints**: All tool functions must have explicit return type hints (e.g., `-> dict[str, Any]`) for better MCP schema generation.
- **Read-Only Design**: Primary focus is on operational data retrieval.
