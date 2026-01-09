"""Tests for the tools module.

This module contains unit tests for the MCP tool functions,
verifying that tool execution and error handling work correctly.
"""

from unittest.mock import patch

import pytest

from nornir_mcp.tools import get_device_data, run_cli_commands


@pytest.mark.asyncio
async def test_get_device_data_success():
    """Test successful execution of the get_device_data tool function.

    Verifies that the tool function properly executes and returns
    the expected result structure when the operation succeeds.
    """
    with (
        patch("nornir_mcp.tools.get_nornir") as mock_get_nornir,
        patch("nornir_mcp.tools.NapalmRunner") as MockRunner,
    ):
        # Mock the get_nornir function to return a mock Nornir instance
        mock_nornir_instance = mock_get_nornir.return_value

        mock_instance = MockRunner.return_value
        # Return a plain dict instead of a Success object
        mock_instance.run_getter.return_value = {"host1": "data"}

        result = await get_device_data("facts")

        assert "error" not in result
        assert result["backend"] == "napalm"
        assert result["data_type"] == "facts"
        assert result["target"] == "all"
        assert result["data"] == {"host1": "data"}
        mock_instance.run_getter.assert_called_once_with("facts", host_name=None, group_name=None)
        MockRunner.assert_called_once_with(mock_nornir_instance)


@pytest.mark.asyncio
async def test_get_device_data_invalid_params():
    """Test invalid parameters handling in the get_device_data tool function.

    Verifies that the tool function properly validates parameters and returns
    the expected error response when invalid parameters are provided.
    """
    result = await get_device_data("facts", host_name="h1", group_name="g1")
    assert result["error"] == "invalid_parameters"


@pytest.mark.asyncio
async def test_run_cli_commands_success():
    """Test successful execution of the run_cli_commands tool function.

    Verifies that the tool function properly executes and returns
    the expected result structure when the operation succeeds.
    """
    with (
        patch("nornir_mcp.tools.get_nornir") as mock_get_nornir,
        patch("nornir_mcp.tools.NetmikoRunner") as MockRunner,
    ):
        # Mock the get_nornir function to return a mock Nornir instance
        mock_nornir_instance = mock_get_nornir.return_value

        mock_instance = MockRunner.return_value
        # Return a plain dict instead of a Success object
        mock_instance.run_command.return_value = {"host1": "output"}

        result = await run_cli_commands("show version")

        assert "error" not in result
        assert result["backend"] == "netmiko"
        assert result["commands"] == "show version"
        assert result["target"] == "all"
        assert result["data"] == {"host1": "output"}
        mock_instance.run_command.assert_called_once_with("show version", host_name=None, group_name=None)
        MockRunner.assert_called_once_with(mock_nornir_instance)


@pytest.mark.asyncio
async def test_run_cli_commands_invalid_params():
    """Test invalid parameters handling in the run_cli_commands tool function.

    Verifies that the tool function properly validates parameters and returns
    the expected error response when invalid parameters are provided.
    """
    result = await run_cli_commands("cmd", host_name="h1", group_name="g1")
    assert result["error"] == "invalid_parameters"
