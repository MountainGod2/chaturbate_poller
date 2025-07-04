"""Integration tests for backoff configuration with client."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import Request, Response

from chaturbate_poller.config.backoff import BackoffConfig
from chaturbate_poller.core.client import ChaturbateClient

from .constants import TEST_URL, TOKEN, USERNAME


class TestBackoffConfigIntegration:
    """Integration tests for backoff configuration with ChaturbateClient."""

    @pytest.mark.asyncio
    async def test_backoff_config_used_by_client(
        self, http_client_mock: Any, disabled_backoff_config: BackoffConfig
    ) -> None:
        """Test that the client uses the backoff configuration correctly."""
        # Set up a server error response
        http_client_mock.return_value = Response(
            status_code=500,
            request=Request(method="GET", url=TEST_URL),
        )

        # Create a client with disabled backoff for fast testing
        async with ChaturbateClient(
            USERNAME, TOKEN, backoff_config=disabled_backoff_config
        ) as client:
            # Verify the client uses the provided config
            assert client.backoff_config is disabled_backoff_config
            assert client.backoff_config.enabled is False

    def test_backoff_config_instance_independence(self) -> None:
        """Test that BackoffConfig instances are independent of each other."""
        # Each BackoffConfig() creates a new instance
        config1 = BackoffConfig()
        config2 = BackoffConfig()

        assert config1 is not config2

        # Modifying one doesn't affect the other
        config1.enabled = False
        assert config1.enabled is False
        assert config2.enabled is True  # Still default

    @pytest.mark.asyncio
    async def test_client_uses_injected_backoff_config(self) -> None:
        """Test that the client properly uses the injected backoff configuration."""
        # Create a custom backoff config
        custom_config = BackoffConfig()
        custom_config.max_tries = 3
        custom_config.base = 1.5

        # Create client with custom config
        async with ChaturbateClient(USERNAME, TOKEN, backoff_config=custom_config) as client:
            # Verify the client uses the custom config
            assert client.backoff_config is custom_config
            assert client.backoff_config.max_tries == 3
            assert client.backoff_config.base == 1.5

    @pytest.mark.asyncio
    async def test_client_uses_default_config_when_none_provided(self) -> None:
        """Test that the client creates a default config when none is provided."""
        # Create client without explicit backoff config
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            # Verify the client has a default config
            assert client.backoff_config is not None
            assert isinstance(client.backoff_config, BackoffConfig)
            assert client.backoff_config.enabled is True

    def test_backoff_config_callable_methods_work_independently(self) -> None:
        """Test that BackoffConfig property access works on independent instances."""
        config1 = BackoffConfig()
        config2 = BackoffConfig()

        # Disable one config
        config1.disable_for_tests()

        # Check that properties return different values
        assert config1.max_tries == 1  # Disabled
        assert config2.max_tries == 6  # Enabled (default)

        assert config1.base == 1  # Disabled
        assert config2.base == 2.0  # Enabled (default)
