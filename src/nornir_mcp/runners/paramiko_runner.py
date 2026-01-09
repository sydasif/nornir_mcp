"""Paramiko runner module for Nornir MCP.

This module defines the ParamikoRunner class, which handles execution
of SSH commands and file operations using nornir-paramiko for Linux server management.
"""

import os
import tarfile
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any

from nornir.core.task import Task
from nornir_paramiko.plugins.tasks import paramiko_command, paramiko_sftp

from nornir_mcp.constants import ErrorType

from .base_runner import BaseRunner


class ParamikoRunner(BaseRunner):
    """Runner for Paramiko automation backend.

    Handles execution of SSH commands and SFTP file operations against Linux servers
    using the nornir-paramiko plugin (which internally uses Paramiko but through Nornir's task system).
    """

    def run_ssh_command(
        self,
        command: str,
        host_name: str | None = None,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Execute an SSH command on target hosts.

        Args:
            command: The command to execute
            host_name: Specific host name to target, or None for all hosts
            group_name: Specific group to target, or None for all hosts

        Returns:
            Dictionary containing command results

        Raises:
            MCPException: If the operation fails

        """
        if not command:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Command parameter is required")

        def ssh_command_task(task: Task):
            """Execute SSH command on a single host using nornir-paramiko.

            This is an internal task function that runs on individual hosts during
            SSH command execution. It handles the actual command execution and
            result processing for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing command execution results with keys:
                    - command: The executed command
                    - stdout: Standard output from the command
                    - stderr: Standard error output from the command
                    - exit_status: Exit code of the command
                    - success: Boolean indicating if the command was successful
                    - error: Error type if command failed
                    - message: Error message if command failed
            """
            try:
                # Execute the command using nornir-paramiko's paramiko_command task
                # Note: paramiko_command doesn't accept timeout parameter
                result = task.run(task=paramiko_command, command=command)

                # CHECK FOR TASK FAILURE FIRST
                if result.failed:
                    return {
                        "command": command,
                        "error": ErrorType.EXECUTION_ERROR,
                        "message": (
                            f"Command execution failed: {str(result.exception)}"
                            if result.exception
                            else "Unknown execution failure"
                        ),
                        "success": False,
                    }

                # Extract results from the nornir result object
                # The result may be different depending on the underlying implementation
                if hasattr(result.result, "stdout"):
                    stdout_data = result.result.stdout
                    stderr_data = result.result.stderr if hasattr(result.result, "stderr") else ""
                    exit_status = result.result.exit_code if hasattr(result.result, "exit_code") else 0
                elif isinstance(result.result, str):
                    # For simple string results
                    stdout_data = result.result
                    stderr_data = ""
                    exit_status = 0
                else:
                    # Handle other result types
                    stdout_data = str(result.result)
                    stderr_data = ""
                    exit_status = 0

                # Return the results
                return {
                    "command": command,
                    "stdout": stdout_data,
                    "stderr": stderr_data,
                    "exit_status": exit_status,
                    "success": exit_status == 0,
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Command execution failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=ssh_command_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_ssh_data(task_output: Any) -> Any:
                """Extractor function for SSH command results.

                This function extracts the relevant data from SSH command task output.

                Args:
                    task_output: Raw output from the SSH command task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
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

        def sftp_upload_task(task: Task):
            """Upload a file to a single host via SFTP using nornir-paramiko.

            This is an internal task function that runs on individual hosts during
            SFTP upload operations. It handles the actual file upload for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing upload results with keys:
                    - local_path: Path of the source file
                    - remote_path: Path of the destination file
                    - success: Boolean indicating if the upload was successful
                    - message: Status message
                    - error: Error type if upload failed
            """
            try:
                # Use nornir-paramiko's sftp task to upload the file
                # Note: paramiko_sftp expects 'action' parameter, not 'operation'
                task.run(task=paramiko_sftp, src=local_path, dst=remote_path, action="put")

                # Return success result
                return {
                    "local_path": local_path,
                    "remote_path": remote_path,
                    "success": True,
                    "message": f"File uploaded successfully to {task.host.name}",
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File upload failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=sftp_upload_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                """Extractor function for file upload results.

                This function extracts the relevant data from file upload task output.

                Args:
                    task_output: Raw output from the file upload task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
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

        def sftp_download_task(task: Task):
            """Download a file from a single host via SFTP using nornir-paramiko.

            This is an internal task function that runs on individual hosts during
            SFTP download operations. It handles the actual file download for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing download results with keys:
                    - remote_path: Path of the source file
                    - local_path: Path of the destination file
                    - success: Boolean indicating if the download was successful
                    - message: Status message
                    - error: Error type if download failed
            """
            try:
                # Create a unique local path for each host to avoid conflicts
                local_file_path = local_path
                if len(task.nornir.inventory.hosts) > 1:
                    # If multiple hosts, append hostname to avoid conflicts
                    path_obj = Path(local_path)
                    local_file_path = str(path_obj.parent / f"{task.host.name}_{path_obj.name}")

                # Use nornir-paramiko's sftp task to download the file
                # Note: paramiko_sftp expects 'action' parameter, not 'operation'
                task.run(task=paramiko_sftp, src=remote_path, dst=local_file_path, action="get")

                # Return success result
                return {
                    "remote_path": remote_path,
                    "local_path": local_file_path,
                    "success": True,
                    "message": f"File downloaded successfully from {task.host.name} to {local_file_path}",
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File download failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=sftp_download_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                """Extractor function for file download results.

                This function extracts the relevant data from file download task output.

                Args:
                    task_output: Raw output from the file download task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
        """Upload a file to target hosts via SFTP (using paramiko_sftp as replacement for SCP).

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

        def scp_upload_task(task: Task):
            """Upload a file to a single host via SFTP using nornir-paramiko.

            This is an internal task function that runs on individual hosts during
            SCP upload operations (using SFTP as replacement). It handles the actual
            file upload for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing upload results with keys:
                    - local_path: Path of the source file
                    - remote_path: Path of the destination file
                    - success: Boolean indicating if the upload was successful
                    - message: Status message
                    - error: Error type if upload failed
            """
            try:
                # Use nornir-paramiko's sftp task to upload the file (replacing SCP)
                task.run(task=paramiko_sftp, src=local_path, dst=remote_path, action="put")

                # Return success result
                return {
                    "local_path": local_path,
                    "remote_path": remote_path,
                    "success": True,
                    "message": f"File uploaded successfully to {task.host.name}",
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File upload failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_upload_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                """Extractor function for file upload results.

                This function extracts the relevant data from file upload task output.

                Args:
                    task_output: Raw output from the file upload task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
        """Download a file from target hosts via SFTP (using paramiko_sftp as replacement for SCP).

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

        def scp_download_task(task: Task):
            """Download a file from a single host via SFTP using nornir-paramiko.

            This is an internal task function that runs on individual hosts during
            SCP download operations (using SFTP as replacement). It handles the actual
            file download for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing download results with keys:
                    - remote_path: Path of the source file
                    - local_path: Path of the destination file
                    - success: Boolean indicating if the download was successful
                    - message: Status message
                    - error: Error type if download failed
            """
            try:
                # Create a unique local path for each host to avoid conflicts
                local_file_path = local_path
                if len(task.nornir.inventory.hosts) > 1:
                    # If multiple hosts, append hostname to avoid conflicts
                    path_obj = Path(local_path)
                    local_file_path = str(path_obj.parent / f"{task.host.name}_{path_obj.name}")

                # Use nornir-paramiko's sftp task to download the file (replacing SCP)
                task.run(task=paramiko_sftp, src=remote_path, dst=local_file_path, action="get")

                # Return success result
                return {
                    "remote_path": remote_path,
                    "local_path": local_file_path,
                    "success": True,
                    "message": f"File downloaded successfully from {task.host.name} to {local_file_path}",
                }
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"File download failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_download_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                """Extractor function for file download results.

                This function extracts the relevant data from file download task output.

                Args:
                    task_output: Raw output from the file download task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
        """Upload a directory to target hosts via SFTP recursively (using paramiko_sftp as replacement).

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
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")

        # Validate local directory exists
        if not os.path.exists(local_path):
            self.raise_error(ErrorType.INVALID_PARAMETERS, f"Local directory does not exist: {local_path}")

        def scp_upload_recursive_task(task: Task):
            """Upload a directory to a single host via SSH command (replacing recursive SCP).

            This is an internal task function that runs on individual hosts during
            recursive directory upload operations. It handles the compression, upload,
            and extraction of directories for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing upload results with keys:
                    - local_path: Path of the source directory
                    - remote_path: Path of the destination directory
                    - success: Boolean indicating if the upload was successful
                    - message: Status message
                    - error: Error type if upload failed
            """
            try:
                # Create a temporary tar file of the directory
                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
                    temp_path = tmp_file.name

                # Create a tar.gz archive of the local directory
                with tarfile.open(temp_path, "w:gz") as tar:
                    tar.add(local_path, arcname=os.path.basename(local_path))

                try:
                    # Upload the archive using paramiko_sftp
                    # Using /tmp/ is intentional for temporary file transfer to remote system
                    task.run(
                        task=paramiko_sftp,
                        src=temp_path,
                        dst=f"/tmp/{os.path.basename(temp_path)}",  # noqa: S108
                        action="put",
                    )

                    # Extract the archive on the remote host using an SSH command
                    extract_cmd = (
                        f'mkdir -p "{remote_path}" && '
                        f'cd "{remote_path}" && '
                        f'tar -xzf "/tmp/{os.path.basename(temp_path)}" && '
                        f'rm "/tmp/{os.path.basename(temp_path)}"'
                    )

                    # Execute the extraction command
                    task.run(task=paramiko_command, command=extract_cmd)

                    return {
                        "local_path": local_path,
                        "remote_path": remote_path,
                        "success": True,
                        "message": f"Directory uploaded successfully to {task.host.name}",
                    }
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_path)
            except Exception as e:
                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Directory upload failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_upload_recursive_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_upload_data(task_output: Any) -> Any:
                """Extractor function for file upload results.

                This function extracts the relevant data from file upload task output.

                Args:
                    task_output: Raw output from the file upload task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
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
    ) -> dict[str, Any]:  # noqa: C901
        """Download a directory from target hosts via SFTP recursively (using paramiko_sftp as replacement).

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
        if not remote_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Remote path parameter is required")
        if not local_path:
            self.raise_error(ErrorType.INVALID_PARAMETERS, "Local path parameter is required")

        def scp_download_recursive_task(task: Task):
            """Download a directory from a single host via SSH command (replacing recursive SCP).

            This is an internal task function that runs on individual hosts during
            recursive directory download operations. It handles the archiving, download,
            and extraction of directories for a single host.

            Args:
                task: The Nornir task object for the current host

            Returns:
                dict: Dictionary containing download results with keys:
                    - remote_path: Path of the source directory
                    - local_path: Path of the destination directory
                    - success: Boolean indicating if the download was successful
                    - message: Status message
                    - error: Error type if download failed
            """
            try:
                # Create a temporary tar file to store the archive
                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
                    temp_path = tmp_file.name

                # Create a tar.gz archive of the remote directory using SSH command
                archive_name = f"temp_archive_{task.host.name}.tar.gz"

                # Archive the remote directory
                archive_cmd = (
                    f"cd /tmp && "
                    f'tar -czf "{archive_name}" '
                    f'-C "{os.path.dirname(remote_path)}" '
                    f'"{os.path.basename(remote_path)}"'
                )

                # Execute the archiving command
                task.run(task=paramiko_command, command=archive_cmd)

                # Download the archive using paramiko_sftp
                # Using /tmp/ is intentional for temporary file transfer from remote system
                task.run(
                    task=paramiko_sftp,
                    src=f"/tmp/{archive_name}",  # noqa: S108
                    dst=temp_path,
                    action="get",
                )

                # Create the local destination directory
                local_dir_path = local_path
                if len(task.nornir.inventory.hosts) > 1:
                    # If multiple hosts, append hostname to avoid conflicts
                    path_obj = Path(local_path)
                    local_dir_path = str(path_obj.parent / f"{task.host.name}_{path_obj.name}")

                os.makedirs(local_dir_path, exist_ok=True)

                # Extract the archive locally with path traversal protection
                with tarfile.open(temp_path, "r:gz") as tar:

                    def is_safe_extract(member: tarfile.TarInfo, extract_path: str) -> bool:
                        """Check if a tar archive member is safe to extract (prevent path traversal).

                        This function implements path traversal protection by ensuring that
                        extracted files remain within the intended destination directory.

                        Args:
                            member: TarInfo object representing the archive member
                            extract_path: Base path where extraction should occur

                        Returns:
                            bool: True if the path is safe to extract, False otherwise
                        """
                        member_path = os.path.abspath(os.path.join(extract_path, member.name))
                        extract_path = os.path.abspath(extract_path)
                        return member_path.startswith(extract_path + os.sep) or member_path == extract_path

                    for member in tar.getmembers():
                        if not is_safe_extract(member, local_dir_path):
                            raise ValueError(f"Unsafe path in archive: {member.name}")

                    tar.extractall(path=local_dir_path)  # noqa: S202

                # Remove the remote archive
                cleanup_cmd = f'rm "/tmp/{archive_name}"'
                task.run(task=paramiko_command, command=cleanup_cmd)

                # Clean up the temporary file
                os.unlink(temp_path)

                return {
                    "remote_path": remote_path,
                    "local_path": local_dir_path,
                    "success": True,
                    "message": f"Directory downloaded successfully from {task.host.name} to {local_dir_path}",
                }
            except Exception as e:
                # Attempt to clean up temp files in case of error
                with suppress(OSError):
                    os.unlink(temp_path)

                return {
                    "error": ErrorType.EXECUTION_ERROR,
                    "message": f"Directory download failed: {str(e)}",
                    "success": False,
                }

        try:
            # Use the parent class method to run the task on hosts
            aggregated_result = self.run_on_hosts(
                task=scp_download_recursive_task, host_name=host_name, group_name=group_name
            )

            # Define an extractor to handle the results properly
            def extract_download_data(task_output: Any) -> Any:
                """Extractor function for file download results.

                This function extracts the relevant data from file download task output.

                Args:
                    task_output: Raw output from the file download task

                Returns:
                    The task output unchanged (passthrough extractor)
                """
                return task_output

            return self.process_results(aggregated_result, extractor=extract_download_data)

        except Exception as error:
            self.raise_error(ErrorType.EXECUTION_ERROR, str(error))
