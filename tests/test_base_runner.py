from unittest.mock import MagicMock

import pytest

from nornir_mcp.constants import ErrorType
from nornir_mcp.nornir_init import NornirManager
from nornir_mcp.runners.base_runner import BaseRunner


class ConcreteRunner(BaseRunner):
    def execute(self, **kwargs):
        return {"data": "test"}


def test_concrete_runner_instantiation():
    """Test that a concrete implementation can be instantiated."""
    manager = MagicMock(spec=NornirManager)
    runner = ConcreteRunner(manager)
    assert isinstance(runner, BaseRunner)


def test_process_results_no_hosts(mock_manager):
    runner = ConcreteRunner(mock_manager)
    # Now process_results raises an exception instead of returning a Result
    from nornir_mcp.types import MCPException
    try:
        result = runner.process_results({})
        # If we reach this line, the exception wasn't raised
        assert False, "Expected MCPException was not raised"
    except MCPException as e:
        assert e.error_type == ErrorType.NO_HOSTS.value  # Compare to string value, not enum
        assert e.message == "No hosts found for the given target."
