"""Tests for the Base runner module.

This module contains unit tests for the BaseRunner class and its methods,
verifying that common functionality works correctly.
"""

from unittest.mock import MagicMock

import pytest
from nornir.core import Nornir

from nornir_mcp.constants import ErrorType
from nornir_mcp.runners.base_runner import BaseRunner
from nornir_mcp.types import MCPException


class TestRunner(BaseRunner):
    """Concrete implementation of BaseRunner for testing purposes."""


def test_base_runner_instantiation():
    """Test that BaseRunner can be instantiated directly now that it's not abstract."""
    nornir_instance = MagicMock(spec=Nornir)
    runner = TestRunner(nornir_instance)
    assert isinstance(runner, BaseRunner)


def test_process_results_no_hosts(mock_nornir):
    """Test process_results method when no hosts are found.

    Verifies that the process_results method properly raises an
    MCPException when no hosts are found for the given target.

    Args:
        mock_nornir: Mocked Nornir instance for testing

    """
    runner = TestRunner(mock_nornir)
    # Now process_results raises an exception instead of returning a Result

    with pytest.raises(MCPException) as exc_info:
        runner.process_results({})

    assert exc_info.value.error_type == ErrorType.NO_HOSTS  # Compare to string value, not enum
    assert exc_info.value.message == "No hosts found for the given target."
