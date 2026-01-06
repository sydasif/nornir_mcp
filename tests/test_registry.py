from unittest.mock import MagicMock

import pytest

from nornir_mcp.runners.base_runner import BaseRunner
from nornir_mcp.runners.registry import RunnerRegistry


def test_registry_register_and_get():
    registry = RunnerRegistry()
    mock_runner = MagicMock(spec=BaseRunner)

    registry.register("test", mock_runner)
    assert registry.get("test") is mock_runner
    assert "test" in registry.list_runners()


def test_registry_duplicate_register():
    registry = RunnerRegistry()
    mock_runner = MagicMock(spec=BaseRunner)

    registry.register("test", mock_runner)
    with pytest.raises(ValueError, match="already registered"):
        registry.register("test", mock_runner)


def test_registry_not_found():
    registry = RunnerRegistry()
    with pytest.raises(KeyError, match="not found"):
        registry.get("unknown")
