from unittest.mock import MagicMock

import pytest

from nornir_mcp.nornir_init import NornirManager


@pytest.fixture
def mock_nornir():
    return MagicMock()


@pytest.fixture
def mock_manager(mock_nornir):
    manager = MagicMock(spec=NornirManager)
    manager.get.return_value = mock_nornir
    return manager
