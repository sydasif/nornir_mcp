"""Test configuration and fixtures for the Nornir MCP server.

This module contains pytest fixtures and configuration used across
all test modules in the test suite.
"""

from unittest.mock import MagicMock

import pytest
from nornir.core import Nornir


@pytest.fixture
def mock_nornir():
    """Provide a mock Nornir instance for testing.

    Returns:
        MagicMock: A mock object that behaves like a Nornir instance

    """
    return MagicMock(spec=Nornir)
