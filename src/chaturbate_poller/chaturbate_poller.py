# chaturbate_poller/src/chaturbate_poller/chaturbate_poller.py
"""Chaturbate poller."""

from __future__ import annotations

import logging

import backoff
import httpx
from httpx import HTTPStatusError, RequestError
from typing_extensions import Self

from .constants import API_TIMEOUT, BASE_URL, ERROR_RANGE_END, ERROR_RANGE_START
from .models import EventsAPIResponse

logger = logging.getLogger(__name__)


class ChaturbateClient:
    """Client for fetching Chaturbate events."""

    def __init__(self, username: str, token: str, timeout: int | None = None) -> None:
        """Initialize client."""
        if not username or not token:
            msg = "Chaturbate username and token are required."
            raise ValueError(msg)
        self.base_url = BASE_URL
        self.timeout = timeout or API_TIMEOUT
        self.username = username
        self.token = token
        self.client = httpx.AsyncClient()

    async def __aenter__(self) -> Self:
        """Enter client."""
        if self.client.is_closed:
            self.client = httpx.AsyncClient()
            logger.debug("HTTP client re-opened.")
        logger.debug("Client opened.")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # noqa: ANN001
        """Exit client."""
        await self.client.aclose()
        logger.debug("Client closed.")

    @backoff.on_exception(
        backoff.expo,
        (HTTPStatusError, RequestError),
        max_time=20,
        giveup=lambda e: not need_retry(e),
        on_backoff=lambda details: logger.debug(
            "Backoff triggered. Retry: %s, Waiting: %s sec. before retrying.",
            details.get("tries", ""),
            int(details.get("wait", 0)),
        ),
        on_giveup=lambda details: logger.debug(
            "Retry stopped: %s after %s attempts.",
            details.get("exception", ""),
            details.get("tries", ""),
        ),
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events."""
        if not url:
            url = (
                f"{self.base_url.format(username=self.username, token=self.token)}?timeout={self.timeout}"  # noqa: E501
                if self.timeout
                else self.base_url.format(username=self.username, token=self.token)
            )
        logger.debug("Fetching events from %s", url)

        response = await self.client.get(url, timeout=None)
        response.raise_for_status()
        return EventsAPIResponse.model_validate(response.json())


def need_retry(exception: Exception) -> bool:
    """Retries requests on 500 series errors."""
    return (
        isinstance(exception, HTTPStatusError)
        and ERROR_RANGE_START <= exception.response.status_code < ERROR_RANGE_END
    )
