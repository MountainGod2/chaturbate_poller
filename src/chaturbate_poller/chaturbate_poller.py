"""Chaturbate poller module."""

from __future__ import annotations

import logging
from types import TracebackType  # noqa: TCH003

import backoff
import httpx
from httpx import HTTPStatusError, RequestError
from typing_extensions import Self

from .constants import BASE_URL, ERROR_RANGE_END, ERROR_RANGE_START
from .models import EventsAPIResponse

logger = logging.getLogger(__name__)


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Args:
        username: Chaturbate username.
        token: Chaturbate token.
        timeout: Timeout in seconds for the API request.

    Attributes:
        base_url: Base URL for the Chaturbate API.
        timeout: Timeout in seconds for the API request.
        username: Chaturbate username.
        token: Chaturbate token.
        client: HTTPX AsyncClient instance.
    """

    def __init__(self, username: str, token: str, timeout: int | None = None) -> None:
        """Initialize client.

        Raises:
            ValueError: If username or token are not provided.
        """
        if not username or not token:
            error_msg = "Chaturbate username and token are required."
            raise ValueError(error_msg)
        self.base_url = BASE_URL
        self.timeout = timeout
        self.username = username
        self.token = token
        self.client = httpx.AsyncClient()

    async def __aenter__(self) -> Self:
        """Enter client.

        Returns:
            ChaturbateClient: Client instance.
        """
        self.client = httpx.AsyncClient()
        logger.debug("Client opened.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit client.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Traceback.
        """
        await self.client.aclose()

    @backoff.on_exception(
        backoff.expo,
        (HTTPStatusError, RequestError),
        max_time=20,
        giveup=lambda e: not need_retry(e),
        on_backoff=lambda details: logger.info(
            "Backoff triggered. Retry: %s, Waiting: %s sec. before retrying.",
            details.get("tries", ""),
            int(details.get("wait", 0)),
        ),
        on_giveup=lambda details: logger.info(
            "Retry stopped: %s after %s attempts.",
            details.get("exception", ""),
            details.get("tries", ""),
        ),
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from the Chaturbate API.

        Args:
            url: URL to fetch events from.

        Returns:
            EventsAPIResponse: Response from the API.

        Raises:
            HTTPStatusError: If the response status code is in the error range.
            RequestError: If an error occurs during the request.
        """
        if url is None:
            url = self._construct_url()
        response = await self.client.get(url, timeout=self.timeout)
        response.raise_for_status()
        return EventsAPIResponse.model_validate(response.json())

    def _construct_url(self) -> str:
        """Construct URL with username, token, and timeout.

        Returns:
            str: Constructed URL.
        """
        base_url = self.base_url.format(username=self.username, token=self.token)
        if self.timeout:
            return f"{base_url}?timeout={self.timeout}"
        return base_url


def need_retry(exception: Exception) -> bool:
    """Retries requests on 500 series errors.

    Args:
        exception: Exception raised by the request.

    Returns:
        bool: True if the request should be retried, False otherwise.
    """
    if isinstance(exception, HTTPStatusError):
        status_code = exception.response.status_code
        return ERROR_RANGE_START <= status_code < ERROR_RANGE_END
    return False
