from typing import Any

import pytest
from httpx import (
    Request,
    Response,
)
from pydantic import ValidationError

from chaturbate_poller.chaturbate_client import ChaturbateClient

from .constants import TEST_URL


class TestEventFetching:
    """Tests for fetching events."""

    @pytest.mark.asyncio
    async def test_fetch_events_undefined_json(
        self, chaturbate_client: ChaturbateClient, http_client_mock: Any
    ) -> None:
        """Test fetching events with undefined JSON."""
        request = Request("GET", TEST_URL)
        response_content = b'{"not": "json", "nextUrl": "https://example.com"}'
        http_client_mock.return_value = Response(200, content=response_content, request=request)
        with pytest.raises(ValidationError, match="1 validation error for EventsAPIResponse"):
            await chaturbate_client.fetch_events(TEST_URL)

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient, caplog: Any
    ) -> None:
        """Test unauthorized access."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(
            401,
            content=b'{"not": "json", "nextUrl": "https://example.com"}',
            request=request,
        )
        await chaturbate_client.fetch_events(TEST_URL)
        assert "Giving up after 1 tries due to server error code 401: Unknown error" in caplog.text

    @pytest.mark.asyncio
    async def test_http_status_error(
        self, http_client_mock: Any, chaturbate_client: ChaturbateClient, caplog: Any
    ) -> None:
        """Test HTTP status error."""
        request = Request("GET", TEST_URL)
        http_client_mock.return_value = Response(500, request=request)
        await chaturbate_client.fetch_events(TEST_URL)
        assert "Giving up after 6 tries due to server error code 500" in caplog.text
