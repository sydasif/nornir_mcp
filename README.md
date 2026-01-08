# Nornir MCP Server

A **Model Context Protocol (MCP)** server that bridges the gap between Large Language Models (LLMs) and network automation. By leveraging **Nornir**, **NAPALM**, and **Netmiko**, this server allows AI assistants to interact directly with network devices, query inventory, and retrieve real-time operational data through a standardized interface.

## Key Features

* **Inventory Awareness**: Instantly list and filter configured network hosts.
* **Deep Device Insights**: Fetch comprehensive data (facts, interfaces, ARP tables) using NAPALM getters.
* **Direct Command Execution**: Run any CLI command on devices with Netmiko.
* **Explicit Architecture**: Uses dedicated runners for each backend (NAPALM, Netmiko) for clarity and simplicity.
* **Flexible Targeting**: Execute queries against a single specific device or an entire group.
* **Standardized Config**: Built to work with your existing Nornir configuration and inventory files.
* **Style & Consistency**: Follows PEP 8 standards with comprehensive documentation, type hints, and consistent error handling.

## Architecture

The project follows a scalable, object-oriented design to ensure reliability and future-proofing:

* **FastMCP**: Handles the Model Context Protocol communication.
* **Nornir Manager**: A singleton lifecycle manager that handles Nornir initialization and inventory reloading.
* **Runners**: A modular execution layer where specific backend logic (e.g., `NapalmRunner`, `NetmikoRunner`, `ParamikoRunner`) is isolated from the core server.
* **Types**: Strict typing and error schemas (`MCPError`) ensure consistent and safe communication with LLMs.
* **Result Type**: Custom `Success`/`Error` result wrapper for explicit error handling paths.
* **Constants**: Centralized constants and enumerations for consistent error types, backends, and configuration keys.
* **Utils**: Shared utility functions for target formatting, parameter validation, and data extraction.
* **Nornir**: Manages inventory, concurrency, and device connections.
* **NAPALM**: Provides a unified driver layer to interact with various network operating systems using getters.
* **Netmiko**: Provides a way to send raw CLI commands to devices.
* **Paramiko**: Provides SSH command execution and SFTP file operations for Linux server management.

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

The server provides dedicated tools for NAPALM getters, Netmiko commands, and Paramiko-based Linux server management.

* **`get_device_data(getter: str, host_name: str | None = None, group_name: str | None = None)`**
  Executes a specific NAPALM getter on a target device to retrieve structured data.

  **Arguments:**
  * `getter`: The specific data to fetch (e.g., `"facts"`, `"interfaces"`, `"arp_table"`). See `nornir://napalm_getters` for a full list.
  * `host_name`: (Optional) The specific device to target. If omitted, runs against all devices.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`run_cli_commands(command: str, host_name: str | None = None, group_name: str | None = None)`**
  Executes a raw CLI command on a target device using Netmiko.

  **Arguments:**
  * `command`: The exact CLI command to execute (e.g., `"show version"`, `"show ip route"`).
  * `host_name`: (Optional) The specific device to target.
  * `group_name`: (Optional) The specific group to target.

* **`run_shell_command(command: str, host_name: str | None = None, group_name: str | None = None, timeout: int = 30)`**
  Executes an SSH command on target Linux servers using Paramiko.

  **Arguments:**
  * `command`: The SSH command to execute (e.g., `"ls -la"`, `"df -h"`, `"systemctl status nginx"`).
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.
  * `timeout`: Command execution timeout in seconds (default: 30).

* **`paramiko_sftp_upload(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**
  Uploads a file to target Linux servers via SFTP using Paramiko.

  **Arguments:**
  * `local_path`: Path to the local file to upload.
  * `remote_path`: Destination path on the remote servers.
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`paramiko_sftp_download(remote_path: str, local_path: str, host_name: str | None = None, group_name: str | None = None)`**
  Downloads a file from target Linux servers via SFTP using Paramiko.

  **Arguments:**
  * `remote_path`: Path to the remote file to download.
  * `local_path`: Destination path for the downloaded file (directory for multiple servers).
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`paramiko_sftp_list(remote_path: str = ".", host_name: str | None = None, group_name: str | None = None)`**
  Lists files and directories in a remote path on target Linux servers via SFTP using Paramiko.

  **Arguments:**
  * `remote_path`: Remote directory path to list (default: current directory).
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`paramiko_scp_upload(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**
  Uploads a file to target Linux servers via SCP using Paramiko.

  **Arguments:**
  * `local_path`: Path to the local file to upload.
  * `remote_path`: Destination path on the remote servers.
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`paramiko_scp_download(remote_path: str, local_path: str, host_name: str | None = None, group_name: str | None = None)`**
  Downloads a file from target Linux servers via SCP using Paramiko.

  **Arguments:**
  * `remote_path`: Path to the remote file to download.
  * `local_path`: Destination path for the downloaded file (directory for multiple servers).
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

* **`paramiko_scp_upload_recursive(local_path: str, remote_path: str, host_name: str | None = None, group_name: str | None = None)`**
  Uploads a directory to target Linux servers via SCP using Paramiko recursively.

  **Arguments:**
  * `local_path`: Path to the local directory to upload.
  * `remote_path`: Destination path on the remote servers.
  * `host_name`: (Optional) The specific server to target. If omitted, runs against all servers.
  * `group_name`: (Optional) The specific group to target. Cannot be used with `host_name`.

**Example Usage:**

```python
# Get basic facts for all devices using NAPALM
get_device_data(getter="facts")

# Get interfaces for a specific switch using NAPALM
get_device_data(getter="interfaces", host_name="switch-01")

# Get the routing table from a specific router using Netmiko
run_cli_commands(command="show ip route", host_name="router-01")

# Get the running configuration for all devices in the 'core' group
run_cli_commands(command="show running-config", group_name="core")

# Get system information for a specific firewall
run_cli_commands(command="show system", host_name="firewall-01")

# Execute a system command on a Linux server
run_shell_command(command="df -h", host_name="web-server-01")

# Check memory usage on all Linux servers in the 'app-servers' group
run_shell_command(command="free -m", group_name="app-servers")

# Upload a configuration file to a Linux server
paramiko_sftp_upload(local_path="/home/user/nginx.conf", remote_path="/etc/nginx/nginx.conf", host_name="web-server-01")

# Download a log file from a Linux server
paramiko_sftp_download(remote_path="/var/log/app.log", local_path="/tmp/app.log", host_name="app-server-01")

# List files in a directory on a Linux server
paramiko_sftp_list(remote_path="/home/user", host_name="web-server-01")

# List files in the root directory on all app servers
paramiko_sftp_list(remote_path="/", group_name="app-servers")

# Upload a file to a Linux server via SCP
paramiko_scp_upload(local_path="/home/user/config.txt", remote_path="/tmp/config.txt", host_name="web-server-01")

# Download a file from a Linux server via SCP
paramiko_scp_download(remote_path="/etc/hosts", local_path="/backup/hosts_backup.txt", host_name="app-server-01")

# Upload a directory recursively to multiple Linux servers via SCP
paramiko_scp_upload_recursive(local_path="/home/user/scripts/", remote_path="/opt/scripts/", group_name="app-servers")
```

### Resources

The server exposes dynamic resources to help discover capabilities:

* **`nornir://napalm_getters`**
  Returns a list of all valid getter names supported by the NAPALM runner. This is useful for knowing what can be passed to the `get_device_data` tool.

* **`nornir://netmiko_commands`**
  Returns a list of common Netmiko CLI commands and their descriptions. This is useful for knowing what commands can be passed to the `run_cli_commands` tool.

## Security & Testing

* **Read-Only by Default**: The `get_device_data` tool is read-only. `run_cli_commands` can execute configuration commands, so use it with caution.
* **Credentials**: Ensure your Nornir inventory files (`defaults.yaml` or `groups.yaml`) are secured with appropriate file permissions.
* **Lab Environment**: To test safely, you can deploy the container lab provided in the [nornir-mcp-lab](https://github.com/sydasif/nornir-mcp-lab.git) repository.

## License

This project is licensed under the MIT License.