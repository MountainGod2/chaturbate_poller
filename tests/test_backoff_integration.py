"""Integration tests for backoff configuration with client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator

    from chaturbate_poller.core.client import ChaturbateClient

import pytest
from httpx import Request, Response

from chaturbate_poller.config.backoff import BackoffConfig, backoff_config
from chaturbate_poller.exceptions import PollingError

from .constants import TEST_URL


class TestBackoffConfigIntegration:
    """Integration tests for backoff configuration with ChaturbateClient."""

    @pytest.mark.asyncio
    async def test_backoff_config_used_by_client(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test that the client uses the backoff configuration correctly."""
        # Set up a server error response
        http_client_mock.return_value = Response(
            500,
            request=Request("GET", TEST_URL),
        )

        # Disable backoff for this test
        backoff_config.disable_for_tests()

        # Test with backoff disabled
        assert backoff_config.get_max_tries() == 1  # Should be 1 when disabled
        assert backoff_config.get_base() == 1  # Should be 1 when disabled
        assert backoff_config.get_factor() == 0  # Should be 0 when disabled

        with pytest.raises(PollingError, match=r"Unhandled polling error encountered."):
            async with chaturbate_client as client:
                await client.fetch_events(TEST_URL)

    def test_backoff_config_callable_methods_return_correct_values(self) -> None:
        """Test that callable methods return values based on enabled state."""
        # Test when enabled
        backoff_config.enabled = True
        backoff_config.max_tries = 6
        backoff_config.base = 2
        backoff_config.factor = 5
        backoff_config.constant_interval = 2
        backoff_config.read_error_max_tries = 10

        assert backoff_config.get_max_tries() == 6
        assert backoff_config.get_read_error_max_tries() == 10
        assert backoff_config.get_base() == 2
        assert backoff_config.get_factor() == 5
        assert backoff_config.get_constant_interval() == 2

        # Test when disabled
        backoff_config.enabled = False

        assert backoff_config.get_max_tries() == 1  # When disabled, returns 1
        assert backoff_config.get_read_error_max_tries() == 1  # When disabled, returns 1
        assert backoff_config.get_base() == 1  # Falls back to 1 when disabled
        assert backoff_config.get_factor() == 0  # Falls back to 0 when disabled
        assert backoff_config.get_constant_interval() == 0  # Falls back to 0 when disabled

    def test_global_backoff_config_instance(self) -> None:
        """Test that the global backoff_config instance works correctly."""
        # Each BackoffConfig() creates a new instance
        new_instance = BackoffConfig()
        assert new_instance is not backoff_config

        # But the global instance is still available and works
        assert backoff_config.enabled is True
        backoff_config.enabled = False
        assert backoff_config.enabled is False

        # Restore
        backoff_config.enabled = True

    @pytest.fixture(autouse=True)
    def restore_backoff_state(self) -> Generator[None]:
        """Restore backoff config to test-safe state before and after each test."""
        # Reset to default values before each test
        backoff_config.enabled = True
        backoff_config.max_tries = 6
        backoff_config.read_error_max_tries = 5
        backoff_config.base = 2.0
        backoff_config.factor = 2.0
        backoff_config.constant_interval = 10

        yield

        # Restore to default values after each test
        backoff_config.enabled = True
        backoff_config.max_tries = 6
        backoff_config.read_error_max_tries = 5
        backoff_config.base = 2.0
        backoff_config.factor = 2.0
        backoff_config.constant_interval = 10
