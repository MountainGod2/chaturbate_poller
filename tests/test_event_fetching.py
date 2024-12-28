from typing import Any

import pytest
from httpx import Request, Response, TimeoutException
from pydantic import ValidationError

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.exceptions import PollingError

from .constants import TEST_URL


class TestEventFetching:
    """Tests for fetching events."""

    @pytest.mark.asyncio
    async def test_fetch_events_invalid_json(
        self, chaturbate_client: ChaturbateClient, http_client_mock: Any
    ) -> None:
        """Test fetching events with invalid JSON response."""
        request = Request("GET", TEST_URL)
        response_content = b'{"not": "json", "nextUrl": "https://example.com"}'
        http_client_mock.return_value = Response(200, content=response_content, request=request)

        with pytest.raises(ValidationError, match="1 validation error for EventsAPIResponse"):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_unauthorized(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetching events with unauthorized access."""
        http_client_mock.return_value = Response(
            401,
            content=b'{"error": "Unauthorized"}',
            request=Request("GET", TEST_URL),
        )

        with pytest.raises(PollingError, match="Invalid token provided."):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_not_found(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetching events when resource is not found."""
        http_client_mock.return_value = Response(
            404,
            content=b'{"error": "Not Found"}',
            request=Request("GET", TEST_URL),
        )

        with pytest.raises(PollingError, match="Requested resource not found."):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_server_error(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetching events with server error."""
        http_client_mock.return_value = Response(
            500,
            request=Request("GET", TEST_URL),
        )

        with pytest.raises(PollingError, match="Giving up due to unhandled polling error"):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_fetch_events_timeout(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient
    ) -> None:
        """Test fetching events with timeout."""
        http_client_mock.side_effect = TimeoutException(message="Timeout occurred.")

        with pytest.raises(TimeoutError, match="Timeout occurred while fetching events."):
            await chaturbate_client.fetch_events(TEST_URL)

    def test_construct_url(self, chaturbate_client: ChaturbateClient) -> None:
        """Test constructing URL."""
        url = chaturbate_client._construct_url()

        assert url == "https://eventsapi.chaturbate.com/events/testuser/testtoken/"
