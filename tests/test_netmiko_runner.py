"""Tests for the Netmiko runner module.

This module contains unit tests for the NetmikoRunner class and its methods,
verifying that Netmiko-based network operations work correctly.
"""

from unittest.mock import MagicMock

import pytest

from nornir_mcp.runners.netmiko_runner import NetmikoRunner


@pytest.fixture
def runner(mock_nornir):
    """Create a NetmikoRunner instance for testing.

    Args:
        mock_nornir: Mocked Nornir instance for testing

    Returns:
        NetmikoRunner: A runner instance for testing

    """
    return NetmikoRunner(mock_nornir)


def test_run_command_success(runner, mock_nornir):
    """Test successful execution of a Netmiko command operation.

    Verifies that the run_command method properly executes and returns
    the expected data structure when the operation succeeds.

    Args:
        runner: NetmikoRunner instance for testing
        mock_nornir: Mocked Nornir instance for testing

    """
    # Mock the Nornir run result
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

    # The result is now a plain dict instead of a Success object
    assert isinstance(result, dict)
    assert result == {"host1": "command output"}
    mock_nornir.run.assert_called_once()

    # Check arguments passed to run
    call_kwargs = mock_nornir.run.call_args[1]
    assert call_kwargs["command_string"] == "show version"


def test_run_command_failure(runner, mock_nornir):
    """Test Netmiko command operation when it fails.

    Verifies that the run_command method properly handles and returns
    error information when the operation fails.

    Args:
        runner: NetmikoRunner instance for testing
        mock_nornir: Mocked Nornir instance for testing

    """
    # Mock the Nornir run result failure
    mock_agg_result = MagicMock()
    mock_agg_result.__bool__.return_value = True

    mock_task_result = MagicMock()
    mock_task_result.failed = True
    mock_task_result.exception = Exception("Connection error")

    mock_agg_result.items.return_value = [("host1", [mock_task_result])]
    mock_nornir.run.return_value = mock_agg_result

    result = runner.run_command("show version")

    # The result is now a plain dict instead of a Success object, but contains error info for the host
    assert isinstance(result, dict)
    assert "host1" in result
    assert result["host1"]["error"] == "execution_failed"
    assert "Connection error" in result["host1"]["message"]


def test_run_command_kwargs(runner, mock_nornir):
    """Test Netmiko command operation with additional keyword arguments.

    Verifies that the run_command method properly passes additional
    keyword arguments to the underlying Netmiko operation.

    Args:
        runner: NetmikoRunner instance for testing
        mock_nornir: Mocked Nornir instance for testing

    """
    mock_agg_result = MagicMock()
    mock_agg_result.__bool__.return_value = True
    mock_task_result = MagicMock()
    mock_task_result.failed = False
    mock_task_result.result = "output"
    mock_agg_result.items.return_value = [("host1", [mock_task_result])]
    mock_nornir.run.return_value = mock_agg_result

    runner.run_command("show version", enable=True)

    call_kwargs = mock_nornir.run.call_args[1]
    assert call_kwargs["enable"] is True
