from unittest.mock import MagicMock

from nornir_mcp.constants import ErrorType
from nornir_mcp.nornir_init import NornirManager
from nornir_mcp.result import Success
from nornir_mcp.runners.base_runner import BaseRunner


class ConcreteRunner(BaseRunner):
    def execute(self, **kwargs):
        return Success({"data": "test"})


def test_concrete_runner_instantiation():
    """Test that a concrete implementation can be instantiated."""
    manager = MagicMock(spec=NornirManager)
    runner = ConcreteRunner(manager)
    assert isinstance(runner, BaseRunner)


def test_process_results_no_hosts(mock_manager):
    runner = ConcreteRunner(mock_manager)
    result = runner.process_results({})
    # The result is now wrapped in an Error object
    assert result.is_error()
    assert result.error_type == ErrorType.NO_HOSTS.value  # Compare to string value, not enum
    assert result.message == "No hosts found for the given target."
