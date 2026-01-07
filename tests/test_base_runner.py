from unittest.mock import MagicMock

import pytest

from nornir_mcp.constants import ErrorType
from nornir.core import Nornir
from nornir_mcp.runners.base_runner import BaseRunner


class ConcreteRunner(BaseRunner):
    def execute(self, **kwargs):
        return {"data": "test"}


def test_concrete_runner_instantiation():
    """Test that a concrete implementation can be instantiated."""
    nornir_instance = MagicMock(spec=Nornir)
    runner = ConcreteRunner(nornir_instance)
    assert isinstance(runner, BaseRunner)


def test_process_results_no_hosts(mock_nornir):
    runner = ConcreteRunner(mock_nornir)
    # Now process_results raises an exception instead of returning a Result
    from nornir_mcp.types import MCPException

    try:
        result = runner.process_results({})
        # If we reach this line, the exception wasn't raised
        assert False, "Expected MCPException was not raised"
    except MCPException as e:
        assert e.error_type == ErrorType.NO_HOSTS  # Compare to string value, not enum
        assert e.message == "No hosts found for the given target."
