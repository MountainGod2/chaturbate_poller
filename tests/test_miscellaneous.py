from typing import Any

import pytest
from httpx import (
    ReadTimeout,
    Request,
    TimeoutException,
)

from chaturbate_poller.chaturbate_client import ChaturbateClient

from .constants import TEST_URL, TOKEN, USERNAME


class TestMiscellaneous:
    """Miscellaneous tests."""

    @pytest.mark.asyncio
    async def test_chaturbate_client_initialization(self) -> None:
        """Test ChaturbateClient initialization."""
        async with ChaturbateClient(USERNAME, TOKEN) as client:
            assert client.username == USERNAME
            assert client.token == TOKEN

    @pytest.mark.asyncio
    async def test_timeout_handling(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test timeout handling."""
        http_client_mock.side_effect = TimeoutException(
            message="Timeout", request=Request("GET", TEST_URL)
        )
        with pytest.raises(TimeoutException):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_timeout(
        self, mocker: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetch_events method when a timeout occurs."""
        mocker.patch.object(
            chaturbate_client.client, "get", side_effect=ReadTimeout("Request timed out")
        )
        with pytest.raises(ReadTimeout):
            await chaturbate_client.fetch_events()

    @pytest.mark.asyncio
    async def test_fetch_events_unhandled_exception(self, mocker: Any) -> None:
        """Test fetch_events method handles unhandled exceptions properly."""
        mocker.patch("httpx.AsyncClient.get", side_effect=Exception("Unhandled error"))
        with pytest.raises(Exception, match="Unhandled error"):
            async with ChaturbateClient(USERNAME, TOKEN) as client:
                await client.fetch_events()
