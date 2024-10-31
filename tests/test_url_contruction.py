import pytest

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.signal_handler import SignalHandler

from .constants import TEST_URL


class TestURLConstruction:
    """Tests for URL construction."""

    @pytest.mark.asyncio
    async def test_url_construction(
        self, chaturbate_client: ChaturbateClient, signal_handler: SignalHandler
    ) -> None:
        """Test URL construction."""
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed."
        await signal_handler._shutdown()

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout(self, chaturbate_client: ChaturbateClient) -> None:
        """Test URL construction with timeout."""
        chaturbate_client.timeout = 10
        url = chaturbate_client._construct_url()
        assert url == f"{TEST_URL}?timeout=10", "URL should be correctly constructed with timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_zero(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout zero."""
        chaturbate_client.timeout = 0
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed without timeout."

    @pytest.mark.asyncio
    async def test_url_construction_with_timeout_none(
        self, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test URL construction with timeout None."""
        chaturbate_client.timeout = None
        url = chaturbate_client._construct_url()
        assert url == TEST_URL, "URL should be correctly constructed without timeout."
