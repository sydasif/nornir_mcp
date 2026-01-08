"""Tests for the Nornir initialization module.

This module contains unit tests for the Nornir initialization functions,
verifying that singleton pattern and thread safety work correctly.
"""

import threading
from unittest.mock import patch

from nornir_mcp.nornir_init import get_nornir, reset_nornir


def test_get_nornir_initialization():
    """Test that get_nornir initializes and returns a Nornir instance."""
    with (
        patch("nornir_mcp.nornir_init._locate_config_file", return_value="/fake/config.yaml"),
        patch("nornir_mcp.nornir_init.InitNornir") as mock_init_nornir,
    ):
        # Reset the global instance before the test within the mock context
        reset_nornir()

        mock_nornir = mock_init_nornir.return_value
        result = get_nornir()

        assert result is mock_nornir
        mock_init_nornir.assert_called_once()


def test_get_nornir_caching():
    """Test that get_nornir returns the same instance on subsequent calls."""
    with (
        patch("nornir_mcp.nornir_init._locate_config_file", return_value="/fake/config.yaml"),
        patch("nornir_mcp.nornir_init.InitNornir") as mock_init_nornir,
    ):
        # Reset the global instance before the test within the mock context
        reset_nornir()

        result1 = get_nornir()
        result2 = get_nornir()

        assert result1 is result2
        # InitNornir should be called only once due to caching
        assert mock_init_nornir.call_count == 1


def test_thread_safe_get_nornir():
    """Test thread safety of get_nornir function."""
    with (
        patch("nornir_mcp.nornir_init._locate_config_file", return_value="/fake/config.yaml"),
        patch("nornir_mcp.nornir_init.InitNornir") as mock_init_nornir,
    ):
        # Reset the global instance before the test within the mock context
        reset_nornir()

        results = []

        def get_nornir_and_store():
            results.append(get_nornir())

        threads = [threading.Thread(target=get_nornir_and_store) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be the same instance
        for i in range(1, len(results)):
            assert results[i] is results[0]
        # InitNornir should be called only once due to caching
        assert mock_init_nornir.call_count == 1


def test_reset_nornir():
    """Test that reset_nornir recreates the Nornir instance."""
    with (
        patch("nornir_mcp.nornir_init._locate_config_file", return_value="/fake/config.yaml"),
        patch("nornir_mcp.nornir_init.InitNornir") as mock_init_nornir,
    ):
        # Reset the global instance before the test within the mock context
        reset_nornir()

        # First call to get_nornir - assigning to variable to avoid linter error
        # The call is used to initialize and for counting the call
        result1 = get_nornir()
        call_count_after_first = mock_init_nornir.call_count

        # Call reset_nornir to recreate the instance
        reset_nornir()

        # Second call to get_nornir after reset - assigning to variable to avoid linter error
        result2 = get_nornir()

        # Verify that the results are valid Nornir instances (side effect verification)
        assert result1 is not None
        assert result2 is not None

        # After reset, InitNornir should be called again
        assert mock_init_nornir.call_count >= call_count_after_first + 1
