# Nornir MCP Server

MCP (Model Context Protocol) server for Nornir network automation, enabling LLMs to interact with network devices through standardized tools.

## Overview

This project provides an MCP server that exposes Nornir network automation capabilities to LLMs. It allows AI models to query network device information and perform network operations through a standardized interface.

## Features

- **Host Listing**: Retrieve information about all configured network hosts
- **Device Facts**: Gather comprehensive device information (model, serial, OS version, vendor) using NAPALM
- **Targeted Queries**: Query specific devices or all devices in the inventory
- **Network Automation**: Provides programmatic access to network infrastructure

## Architecture

The server uses:

- **FastMCP**: For MCP protocol implementation
- **Nornir**: For network automation framework
- **NAPALM**: For device interaction and fact gathering
- **Containerlab**: For network device simulation (in development environment)

## Tools

### `list_hosts()`

Lists all hosts defined in the Nornir inventory with their names, IP addresses, and platforms.

### `get_network_facts(target_host: str = None)`

Gathers device facts from network equipment using NAPALM. Can target a specific device or retrieve facts from all available devices.

## Configuration

The server reads configuration from:

- `config.yaml`: Nornir configuration
- `hosts.yaml`: Network device definitions
- `groups.yaml`: Device group configurations
- `defaults.yaml`: Default configuration values

## Security Considerations

- Device credentials are managed through Nornir inventory configuration
- Network connectivity requirements must be satisfied for fact gathering
- Device access permissions must be properly configured

## Usage

The server runs as an MCP service and can be connected to by LLM clients that support the MCP protocol. Once connected, the client can invoke the available tools to interact with network devices.

## Development

The project includes a containerlab environment for testing with simulated network devices (router and switch).