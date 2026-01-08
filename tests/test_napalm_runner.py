"""Tests for the Napalm runner module.

This module contains unit tests for the NapalmRunner class and its methods,
verifying that NAPALM-based network operations work correctly.
"""

from unittest.mock import MagicMock, patch

from nornir.core.task import AggregatedResult, MultiResult, Result

from nornir_mcp.runners.napalm_runner import NapalmRunner


def test_run_getter_success(mock_nornir):
    """Test successful execution of a NAPALM getter operation.

    Verifies that the run_getter method properly executes and returns
    the expected data structure when the operation succeeds.

    Args:
        mock_nornir: Mocked Nornir instance for testing

    """
    runner = NapalmRunner(mock_nornir)

    # Mock Nornir run result
    mock_result = MagicMock(spec=AggregatedResult)
    mock_result.__getitem__.return_value = MultiResult("test_task")  # Satisfy type hints if needed
    mock_result.__iter__.return_value = iter(["device1"])
    mock_result.__len__.return_value = 1

    mock_multi_result = MultiResult("test_task")
    mock_task_result = Result(host=MagicMock(), result={"facts": "some_facts"})
    mock_multi_result.append(mock_task_result)

    mock_result.items.return_value = [("device1", mock_multi_result)]

    with patch.object(runner, "run_on_hosts", return_value=mock_result):
        result = runner.run_getter("facts", "device1")
        # The result is now a plain dict instead of a Success object
        assert isinstance(result, dict)
        assert result == {"device1": "some_facts"}


def test_run_getter_extraction(mock_nornir):
    """Test NAPALM getter result extraction functionality.

    Verifies that the run_getter method properly extracts only the requested
    data from the result when the result contains multiple fields.

    Args:
        mock_nornir: Mocked Nornir instance for testing

    """
    runner = NapalmRunner(mock_nornir)

    mock_result = MagicMock(spec=AggregatedResult)
    mock_result.__len__.return_value = 1

    mock_multi_result = MultiResult("test_task")
    # Result contains more than just the getter
    mock_task_result = Result(host=MagicMock(), result={"facts": "target", "other": "ignored"})
    mock_multi_result.append(mock_task_result)

    mock_result.items.return_value = [("device1", mock_multi_result)]

    with patch.object(runner, "run_on_hosts", return_value=mock_result):
        # We asked for 'facts', so we should only get 'target'
        result = runner.run_getter("facts")
        # The result is now a plain dict instead of a Success object
        assert isinstance(result, dict)
        assert result == {"device1": "target"}
