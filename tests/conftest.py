from unittest.mock import MagicMock

import pytest
from nornir.core import Nornir


@pytest.fixture
def mock_nornir():
    return MagicMock(spec=Nornir)
