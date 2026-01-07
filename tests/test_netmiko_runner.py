from unittest.mock import MagicMock

import pytest

from nornir_mcp.runners.netmiko_runner import NetmikoRunner


@pytest.fixture
def mock_manager():
    return MagicMock()


@pytest.fixture
def runner(mock_manager):
    return NetmikoRunner(mock_manager)


def test_run_command_success(runner, mock_manager):
    # Mock the Nornir run result
    mock_nornir = mock_manager.get.return_value
    mock_agg_result = MagicMock()
    # Behave like a dictionary
    mock_agg_result.items.return_value = []
    # But when we iterate, we want it to behave like the real thing

    # Mocking AggregatedResult is tricky because it acts as dict and boolean.
    # BaseRunner.process_results checks 'if not result:' first.
    # So we need __bool__ to return True.
    mock_agg_result.__bool__.return_value = True

    mock_task_result = MagicMock()
    mock_task_result.failed = False
    mock_task_result.result = "command output"

    mock_agg_result.items.return_value = [("host1", [mock_task_result])]
    mock_nornir.run.return_value = mock_agg_result

    result = runner.run_command("show version")

    assert result == {"host1": "command output"}
    mock_nornir.run.assert_called_once()

    # Check arguments passed to run
    call_kwargs = mock_nornir.run.call_args[1]
    assert call_kwargs["command_string"] == "show version"


def test_run_command_failure(runner, mock_manager):
    # Mock the Nornir run result failure
    mock_nornir = mock_manager.get.return_value
    mock_agg_result = MagicMock()
    mock_agg_result.__bool__.return_value = True

    mock_task_result = MagicMock()
    mock_task_result.failed = True
    mock_task_result.exception = Exception("Connection error")

    mock_agg_result.items.return_value = [("host1", [mock_task_result])]
    mock_nornir.run.return_value = mock_agg_result

    result = runner.run_command("show version")

    assert "host1" in result
    assert result["host1"]["error"] == "execution_failed"
    assert "Connection error" in result["host1"]["message"]


def test_run_getter_not_supported(runner):
    result = runner.run_getter("get_facts")
    assert result["error"] == "not_supported"
