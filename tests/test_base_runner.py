from unittest.mock import MagicMock

import pytest

from nornir_mcp.nornir_init import NornirManager
from nornir_mcp.runners.base_runner import BaseRunner
from nornir_mcp.types import MCPError


class ConcreteRunner(BaseRunner):
    def run_getter(self, getter: str, hostname: str | None = None) -> dict | MCPError:
        return {"data": "test"}


def test_base_runner_instantiation():
    """Test that BaseRunner cannot be instantiated directly."""
    manager = MagicMock(spec=NornirManager)
    with pytest.raises(TypeError):
        BaseRunner(manager)


def test_concrete_runner_instantiation():
    """Test that a concrete implementation can be instantiated."""
    manager = MagicMock(spec=NornirManager)
    runner = ConcreteRunner(manager)
    assert isinstance(runner, BaseRunner)


def test_process_results_no_hosts(mock_manager):
    runner = ConcreteRunner(mock_manager)
    result = runner.process_results({})
    assert result == {
        "error": "no_hosts",
        "message": "No hosts found for the given target.",
    }
