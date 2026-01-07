from unittest.mock import patch

from nornir_mcp.tools import run_napalm_getter, run_netmiko_command


def test_run_napalm_getter_success():
    with patch("nornir_mcp.tools.NapalmRunner") as MockRunner:
        mock_instance = MockRunner.return_value
        mock_instance.run_getter.return_value = {"host1": "data"}

        result = run_napalm_getter("get_facts")

        assert "error" not in result
        assert result["backend"] == "napalm"
        assert result["data"] == {"host1": "data"}
        mock_instance.run_getter.assert_called_once_with("get_facts", None, None)


def test_run_napalm_getter_invalid_params():
    result = run_napalm_getter("get_facts", host_name="h1", group_name="g1")
    assert result["error"] == "invalid_parameters"


def test_run_netmiko_command_success():
    with patch("nornir_mcp.tools.NetmikoRunner") as MockRunner:
        mock_instance = MockRunner.return_value
        mock_instance.run_command.return_value = {"host1": "output"}

        result = run_netmiko_command("show version")

        assert "error" not in result
        assert result["backend"] == "netmiko"
        assert result["data"] == {"host1": "output"}
        mock_instance.run_command.assert_called_once_with("show version", None, None)


def test_run_netmiko_command_invalid_params():
    result = run_netmiko_command("cmd", host_name="h1", group_name="g1")
    assert result["error"] == "invalid_parameters"
