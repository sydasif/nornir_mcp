"""Paramiko runner module for Nornir MCP.

This module defines the ParamikoRunner class, which handles execution
of SSH commands and file operations using the Paramiko library for Linux server management.
"""

import os
from pathlib import Path
from typing import Any

import paramiko

# Import the scp module for secure file transfers
try:
    import scp
except ImportError:
    scp = None

from ..constants import ErrorType
from .base_runner import BaseRunner


class ParamikoRunner(BaseRunner):
    """Runner for Paramiko automation backend.

    Handles execution of SSH commands and SFTP file operations against Linux servers
    using the Paramiko library.
    """

    def run_ssh_command(
        self,
        command: str,
        host_name: str | None = None,
        group_name: str | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Execute an SSH command on target hosts.

        Args:
            command: The command to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts
            timeout: SSH command timeout in seconds

        Returns:
            Dictionary containing command results

        Raises:
            MCPException: If the operation fails
        """
        if not command:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Command parameter is required")

        try:
            # Create a custom task for SSH command execution
            def ssh_command_task(task):
                """Execute SSH command on a single host."""
                host = task.host
                hostname = host.hostname or host.name

                # Get SSH connection parameters from host data
                username = host.username
                password = host.password
                port = host.port or 22

                # Create SSH client
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                try:
                    # Connect to the host
                    ssh_client.connect(
                        hostname=hostname,
                        port=port,
                        username=username,
                        password=password,
                        timeout=timeout,
                        look_for_keys=True,  # Allow key-based auth
                        allow_agent=True,  # Allow SSH agent
                    )

                    # Execute the command
                    stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)

                    # Get the results
                    stdout_data = stdout.read().decode("utf-8")
                    stderr_data = stderr.read().decode("utf-8")
                    exit_status = stdout.channel.recv_exit_status()

                    # Return the results
                    return {
                        "command": command,
                        "stdout": stdout_data,
                        "stderr": stderr_data,
                        "exit_status": exit_status,
                        "success": exit_status == 0,
                    }

                except paramiko.AuthenticationException as e:
                    return {
                        "error": ErrorType.EXECUTION_ERROR,
                        "message": f"Authentication failed: {str(e)}",
                        "success": False,
                    }
                except paramiko.SSHException as e:
                    return {
                        "error": ErrorType.EXECUTION_ERROR,
                        "message": f"SSH error: {str(e)}",
                        "success": False,
                    }
                except Exception as e:
                    return {
                        "error": ErrorType.EXECUTION_ERROR,
                        "message": f"Command execution failed: {str(e)}",
                        "success": False,
                    }
                finally:
                    ssh_client.close()

            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=ssh_command_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_ssh_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_ssh_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def sftp_upload(
        self,
        local_path: str,
        remote_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Upload a file to target hosts via SFTP.

        Args:
            local_path: Path to the local file to upload
            remote_path: Destination path on the remote host
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing upload results

        Raises:
            MCPException: If the operation fails
        """
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")

        # Validate local file exists
        if not os.path.exists(local_path):
            self.raise_error(ErrorType.INVALID_PARAMETERS, f"Local file does not exist: {local_path}")

        def sftp_upload_task(task):
            """Upload a file to a single host via SFTP."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SFTP client
                sftp_client = ssh_client.open_sftp()

                # Upload the file
                sftp_client.put(local_path, remote_path)

                # Close SFTP client
                sftp_client.close()

                # Return success result
                return {
                    "local_path": local_path,
                    "remote_path": remote_path,
                    "success": True,
                    "message": f"File uploaded successfully to {hostname}",
                }

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Local file not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File upload failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=sftp_upload_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_upload_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def sftp_download(
        self,
        remote_path: str,
        local_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Download a file from target hosts via SFTP.

        Args:
            remote_path: Path to the remote file to download
            local_path: Destination path for the downloaded file (directory for multiple hosts)
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing download results

        Raises:
            MCPException: If the operation fails
        """
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")

        def sftp_download_task(task):
            """Download a file from a single host via SFTP."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SFTP client
                sftp_client = ssh_client.open_sftp()

                # Create a unique local path for each host to avoid conflicts
                local_file_path = local_path
                if len(task.nornir.inventory.hosts) > 1:
                    # If multiple hosts, append hostname to avoid conflicts
                    path_obj = Path(local_path)
                    local_file_path = str(path_obj.parent / f"{hostname}_{path_obj.name}")

                # Download the file
                sftp_client.get(remote_path, local_file_path)

                # Close SFTP client
                sftp_client.close()

                # Return success result
                return {
                    "remote_path": remote_path,
                    "local_path": local_file_path,
                    "success": True,
                    "message": f"File downloaded successfully from {hostname} to {local_file_path}",
                }

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Remote file not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File download failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=sftp_download_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_download_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def scp_upload(
        self,
        local_path: str,
        remote_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Upload a file to target hosts via SCP.

        Args:
            local_path: Path to the local file to upload
            remote_path: Destination path on the remote host
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing upload results

        Raises:
            MCPException: If the operation fails
        """
        if scp is None:
            self.raise_error(
                ErrorType.EXECUTION_ERROR, "SCP library not available. Please install the 'scp' package."
            )

        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")

        # Validate local file exists
        if not os.path.exists(local_path):
            self.raise_error(ErrorType.INVALID_PARAMETERS, f"Local file does not exist: {local_path}")

        def scp_upload_task(task):
            """Upload a file to a single host via SCP."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SCP client using the SSH transport
                scp_client = scp.SCPClient(ssh_client.get_transport())

                try:
                    # Upload the file
                    scp_client.put(local_path, remote_path)

                    # Return success result
                    return {
                        "local_path": local_path,
                        "remote_path": remote_path,
                        "success": True,
                        "message": f"File uploaded successfully to {hostname}",
                    }
                finally:
                    # Close the SCP client
                    scp_client.close()

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Local file not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except scp.SCPException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SCP error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File upload failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_upload_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_upload_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def scp_download(
        self,
        remote_path: str,
        local_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Download a file from target hosts via SCP.

        Args:
            remote_path: Path to the remote file to download
            local_path: Destination path for the downloaded file (directory for multiple hosts)
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing download results

        Raises:
            MCPException: If the operation fails
        """
        if scp is None:
            self.raise_error(
                ErrorType.EXECUTION_ERROR, "SCP library not available. Please install the 'scp' package."
            )

        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")

        def scp_download_task(task):
            """Download a file from a single host via SCP."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SCP client using the SSH transport
                scp_client = scp.SCPClient(ssh_client.get_transport())

                try:
                    # Create a unique local path for each host to avoid conflicts
                    local_file_path = local_path
                    if len(task.nornir.inventory.hosts) > 1:
                        # If multiple hosts, append hostname to avoid conflicts
                        path_obj = Path(local_path)
                        local_file_path = str(path_obj.parent / f"{hostname}_{path_obj.name}")

                    # Download the file
                    scp_client.get(remote_path, local_file_path)

                    # Return success result
                    return {
                        "remote_path": remote_path,
                        "local_path": local_file_path,
                        "success": True,
                        "message": f"File downloaded successfully from {hostname} to {local_file_path}",
                    }
                finally:
                    # Close the SCP client
                    scp_client.close()

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Remote file not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except scp.SCPException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SCP error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File download failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_download_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_download_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def scp_upload_recursive(
        self,
        local_path: str,
        remote_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Upload a directory to target hosts via SCP recursively.

        Args:
            local_path: Path to the local directory to upload
            remote_path: Destination path on the remote host
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing upload results

        Raises:
            MCPException: If the operation fails
        """
        if scp is None:
            self.raise_error(
                ErrorType.EXECUTION_ERROR, "SCP library not available. Please install the 'scp' package."
            )

        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")

        # Validate local directory exists
        if not os.path.exists(local_path):
            self.raise_error(ErrorType.INVALID_PARAMETERS, f"Local directory does not exist: {local_path}")

        def scp_upload_recursive_task(task):
            """Upload a directory to a single host via SCP recursively."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SCP client using the SSH transport
                scp_client = scp.SCPClient(ssh_client.get_transport())

                try:
                    # Upload the directory recursively
                    scp_client.put(local_path, remote_path, recursive=True)

                    # Return success result
                    return {
                        "local_path": local_path,
                        "remote_path": remote_path,
                        "success": True,
                        "message": f"Directory uploaded successfully to {hostname}",
                    }
                finally:
                    # Close the SCP client
                    scp_client.close()

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Local directory not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except scp.SCPException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SCP error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Directory upload failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_upload_recursive_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_upload_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))

    def scp_download_recursive(
        self,
        remote_path: str,
        local_path: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Download a directory from target hosts via SCP recursively.

        Args:
            remote_path: Path to the remote directory to download
            local_path: Destination path for the downloaded directory
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing download results

        Raises:
            MCPException: If the operation fails
        """
        if scp is None:
            self.raise_error(
                ErrorType.EXECUTION_ERROR, "SCP library not available. Please install the 'scp' package."
            )

        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")

        def scp_download_recursive_task(task):
            """Download a directory from a single host via SCP recursively."""
            host = task.host
            hostname = host.hostname or host.name

            # Get SSH connection parameters from host data
            username = host.username
            password = host.password
            port = host.port or 22

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                # Connect to the host
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30,
                    look_for_keys=True,
                    allow_agent=True,
                )

                # Create SCP client using the SSH transport
                scp_client = scp.SCPClient(ssh_client.get_transport())

                try:
                    # Create a unique local path for each host to avoid conflicts
                    local_dir_path = local_path
                    if len(task.nornir.inventory.hosts) > 1:
                        # If multiple hosts, append hostname to avoid conflicts
                        path_obj = Path(local_path)
                        local_dir_path = str(path_obj.parent / f"{hostname}_{path_obj.name}")

                    # Download the directory recursively
                    scp_client.get(remote_path, local_dir_path, recursive=True)

                    # Return success result
                    return {
                        "remote_path": remote_path,
                        "local_path": local_dir_path,
                        "success": True,
                        "message": f"Directory downloaded successfully from {hostname} to {local_dir_path}",
                    }
                finally:
                    # Close the SCP client
                    scp_client.close()

            except FileNotFoundError as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Remote directory not found: {str(e)}",
                    "success": False,
                }
            except paramiko.AuthenticationException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Authentication failed: {str(e)}",
                    "success": False,
                }
            except paramiko.SSHException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SSH error: {str(e)}",
                    "success": False,
                }
            except scp.SCPException as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"SCP error: {str(e)}",
                    "success": False,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Directory download failed: {str(e)}",
                    "success": False,
                }
            finally:
                ssh_client.close()

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_download_recursive_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                return task_output

            return self.process_results(aggregated_result, extractor=extract_download_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))
