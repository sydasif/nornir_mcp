from unittest.mock import MagicMock

import pytest

from nornir_mcp.runners.base_runner import BaseRunner
from nornir_mcp.tools import get_registry, run_napalm_getter


@pytest.fixture(autouse=True)
def clean_registry():
    """Reset registry before each test."""
    get_registry().reset()


def test_run_getter_unknown_backend():
    result = run_napalm_getter("unknown", "facts")
    assert result["error"] == "unknown_backend"


def test_run_getter_success():
    mock_runner = MagicMock(spec=BaseRunner)
    mock_runner.run_getter.return_value = {"host1": "data"}

    get_registry().register("mock", mock_runner)

    result = run_napalm_getter("mock", "facts")
    assert "error" not in result
    assert result["data"] == {"host1": "data"}
    assert result["backend"] == "mock"
