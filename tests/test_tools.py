import asyncio
from unittest.mock import patch

from nornir_mcp.tools import run_napalm_getter, run_netmiko_command


def test_run_napalm_getter_success():
    with patch("nornir_mcp.tools.get_nornir") as mock_get_nornir, \
         patch("nornir_mcp.tools.NapalmRunner") as MockRunner:
        # Mock the get_nornir function to return a mock Nornir instance
        mock_nornir_instance = mock_get_nornir.return_value

        mock_instance = MockRunner.return_value
        # Return a plain dict instead of a Success object
        mock_instance.run_getter.return_value = {"host1": "data"}

        result = asyncio.run(run_napalm_getter("facts"))

        assert "error" not in result
        assert result["backend"] == "napalm"
        assert result["getter"] == "facts"
        assert result["target"] == "all"
        assert result["data"] == {"host1": "data"}
        mock_instance.run_getter.assert_called_once_with("facts", None, None)
        MockRunner.assert_called_once_with(mock_nornir_instance)


def test_run_napalm_getter_invalid_params():
    result = asyncio.run(run_napalm_getter("facts", host_name="h1", group_name="g1"))
    assert result["error"] == "invalid_parameters"


def test_run_netmiko_command_success():
    with patch("nornir_mcp.tools.get_nornir") as mock_get_nornir, \
         patch("nornir_mcp.tools.NetmikoRunner") as MockRunner:
        # Mock the get_nornir function to return a mock Nornir instance
        mock_nornir_instance = mock_get_nornir.return_value

        mock_instance = MockRunner.return_value
        # Return a plain dict instead of a Success object
        mock_instance.run_command.return_value = {"host1": "output"}

        result = asyncio.run(run_netmiko_command("show version"))

        assert "error" not in result
        assert result["backend"] == "netmiko"
        assert result["command"] == "show version"
        assert result["target"] == "all"
        assert result["data"] == {"host1": "output"}
        mock_instance.run_command.assert_called_once_with("show version", None, None)
        MockRunner.assert_called_once_with(mock_nornir_instance)


def test_run_netmiko_command_invalid_params():
    result = asyncio.run(run_netmiko_command("cmd", host_name="h1", group_name="g1"))
    assert result["error"] == "invalid_parameters"
