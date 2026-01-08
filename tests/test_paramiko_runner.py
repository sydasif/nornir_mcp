"""Tests for the Paramiko runner module.

This module contains unit tests for the ParamikoRunner class and its methods,
verifying that error handling works correctly.
"""

from unittest.mock import Mock

import pytest

from nornir_mcp.constants import ErrorType
from nornir_mcp.runners.paramiko_runner import ParamikoRunner
from nornir_mcp.types import MCPException


class TestParamikoRunner:
    """Test suite for ParamikoRunner class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_nornir = Mock()
        self.runner = ParamikoRunner(self.mock_nornir)

    def test_run_ssh_command_empty_command(self):
        """Test SSH command execution with empty command."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.run_ssh_command("", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Command parameter is required" in exc_info.value.message

    def test_sftp_upload_empty_paths(self):
        """Test SFTP upload with empty paths."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.sftp_upload("", "/remote/path.txt", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Local path parameter is required" in exc_info.value.message

        with pytest.raises(MCPException) as exc_info:
            self.runner.sftp_upload("/local/path.txt", "", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Remote path parameter is required" in exc_info.value.message

    def test_sftp_download_empty_paths(self):
        """Test SFTP download with empty paths."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.sftp_download("", "/local/path.txt", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Remote path parameter is required" in exc_info.value.message

        with pytest.raises(MCPException) as exc_info:
            self.runner.sftp_download("/remote/path.txt", "", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Local path parameter is required" in exc_info.value.message

    def test_scp_upload_empty_paths(self):
        """Test SCP upload with empty paths."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_upload("", "/remote/path.txt", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Local path parameter is required" in exc_info.value.message

        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_upload("/local/path.txt", "", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Remote path parameter is required" in exc_info.value.message

    def test_scp_download_empty_paths(self):
        """Test SCP download with empty paths."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_download("", "/local/path.txt", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Remote path parameter is required" in exc_info.value.message

        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_download("/remote/path.txt", "", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Local path parameter is required" in exc_info.value.message

    def test_scp_upload_recursive_empty_paths(self):
        """Test SCP upload recursive with empty paths."""
        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_upload_recursive("", "/remote/path.txt", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Local path parameter is required" in exc_info.value.message

        with pytest.raises(MCPException) as exc_info:
            self.runner.scp_upload_recursive("/local/path.txt", "", host_name="test-host")

        assert exc_info.value.error_type == ErrorType.INVALID_PARAMETERS
        assert "Remote path parameter is required" in exc_info.value.message


def test_import():
    """Simple test to verify the module can be imported."""
    assert ParamikoRunner is not None
