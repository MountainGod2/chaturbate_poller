import pytest
from httpx import (
    AsyncClient,
)

from chaturbate_poller.chaturbate_client import ChaturbateClient

from .constants import TOKEN, USERNAME


class TestClientLifecycle:
    """Tests for the client lifecycle."""

    @pytest.mark.asyncio
    async def test_client_as_context_manager(self) -> None:
        """Test client as a context manager."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert isinstance(client.client, AsyncClient), (
                "Client should be an instance of AsyncClient during context management."
            )

    @pytest.mark.asyncio
    async def test_client_closed_correctly(self, chaturbate_client: ChaturbateClient) -> None:
        """Test client is closed correctly."""
        async with chaturbate_client:
            await chaturbate_client.client.aclose()
        assert chaturbate_client.client.is_closed, (
            "Client should be closed after exiting context manager."
        )
