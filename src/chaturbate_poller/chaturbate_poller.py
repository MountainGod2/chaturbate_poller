# chaturbate_poller/src/chaturbate_poller/chaturbate_poller.py
"""Chaturbate poller."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import backoff
import httpx
from httpx import HTTPStatusError, RequestError
from typing_extensions import Self

from .constants import API_TIMEOUT, BASE_URL, ERROR_RANGE_END, ERROR_RANGE_START
from .models import EventsAPIResponse

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__package__)
"""logging.Logger: The logger for the module."""
in_test_mode = False
"""bool: Flag to indicate if the module is in test mode."""
max_tries = 2 if in_test_mode else None
"""int: The maximum number of tries for the backoff decorator."""


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Attributes:
        base_url (str): The base URL for the Chaturbate API.
        timeout (int): The timeout for the API request.
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        client (httpx.AsyncClient): The HTTP client.

    """

    def __init__(self, username: str, token: str, timeout: int | None = None) -> None:
        """Initialize client.

        Args:
            username (str): The Chaturbate username.
            token (str): The Chaturbate token.
            timeout (int, optional): The timeout for the API request. Defaults to None.

        Raises:
            ValueError: If username or token are not provided.

        """
        if not username or not token:
            error_message = "Chaturbate username and token are required."
            raise ValueError(error_message)
        self.base_url = BASE_URL
        self.timeout = timeout or API_TIMEOUT
        self.username = username
        self.token = token
        self.client = httpx.AsyncClient()

    async def __aenter__(self) -> Self:
        """Enter client.

        Returns:
            Self: The client instance.

        """
        if self.client.is_closed:
            self.client = httpx.AsyncClient()
            logger.debug("HTTP client re-opened.")
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
            exc_type (type[BaseException]): The exception type.
            exc_value (BaseException): The exception value.
            traceback (TracebackType): The traceback.

        """
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
        """Fetch events.

        Args:
            url (str, optional): The URL to fetch events from. Defaults to None.

        Returns:
            EventsAPIResponse: The events API response.

        """
        if not url:
            url = self.base_url.format(username=self.username, token=self.token)
            if self.timeout:
                url += f"?timeout={self.timeout}"
        logger.debug("Fetching events from %s", url)

        response = await self.client.get(url, timeout=None)
        response.raise_for_status()
        return EventsAPIResponse.model_validate(response.json())


def need_retry(exception: Exception) -> bool:
    """Retries requests on 500 series errors.

    Args:
        exception (Exception): The exception.

    Returns:
        bool: True if the exception is a 500 series error, False otherwise.

    """
    return (
        isinstance(exception, HTTPStatusError)
        and ERROR_RANGE_START <= exception.response.status_code < ERROR_RANGE_END
    )
