"""Chaturbate poller module."""

import logging
from logging.config import dictConfig
from types import TracebackType

import backoff
import httpx
from httpx import HTTPStatusError, RequestError

from chaturbate_poller.constants import BASE_URL, HttpStatusCode
from chaturbate_poller.logging_config import LOGGING_CONFIG
from chaturbate_poller.models import EventsAPIResponse

dictConfig(LOGGING_CONFIG)
"""Use the logging configuration from LOGGING_CONFIG."""

logger = logging.getLogger(__name__)
"""Logger for the module."""


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        timeout (int, optional): The timeout for the request. Defaults to None.
        base_url (str, optional): The base URL for the Chaturbate API. Defaults to None.

    Raises:
        ValueError: If username or token are not provided.
    """

    def __init__(
        self,
        username: str,
        token: str,
        timeout: int | None = None,
        base_url: str | None = None,
    ) -> None:
        """Initialize client.

        Args:
            username (str): The Chaturbate username.
            token (str): The Chaturbate token.
            timeout (int, optional): The timeout for the request. Defaults to None.
            base_url (str, optional): The base URL for the API. Defaults to None.

        Raises:
            ValueError: If username or token are not provided.
        """
        if not username or not token:
            msg = "Chaturbate username and token are required."
            raise ValueError(msg)

        self.base_url = base_url or BASE_URL
        self.timeout = timeout
        self.username = username
        self.token = token
        self.client = httpx.AsyncClient()

    async def __aenter__(self) -> "ChaturbateClient":
        """Enter client.

        Returns:
            ChaturbateClient: The client.
        """
        logger.debug("Client opened.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit client."""
        await self.client.aclose()

    @backoff.on_exception(
        backoff.expo,
        (HTTPStatusError, RequestError),
        max_time=20,
        giveup=lambda e: not need_retry(e),
        on_backoff=lambda details: logger.info(
            "Backoff triggered. Retry: %s, Waiting: %s seconds before retrying.",
            details.get("tries", ""),
            int(details.get("wait", 0)),
        ),
        on_giveup=lambda details: logger.info(
            "Retry stopped after %s attempts.",
            details.get("tries", ""),
        ),
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from the Chaturbate API.

        Args:
            url (str, optional): The URL to fetch events from. Defaults to None.

        Returns:
            EventsAPIResponse: The events API response.
        """
        if url is None:
            url = self._construct_url()
        response = await self.client.get(url, timeout=self.timeout)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == HttpStatusCode.UNAUTHORIZED:
                error_message = "Unauthorized access. Verify the username and token."
                logger.exception(error_message)
                raise ValueError(error_message) from e
            raise
        return EventsAPIResponse.model_validate(response.json())

    def _construct_url(self) -> str:
        """Construct URL with username, token, and timeout.

        Returns:
            str: The constructed URL.
        """
        base_url = self.base_url.format(username=self.username, token=self.token)
        if self.timeout:
            return f"{base_url}?timeout={self.timeout}"
        return base_url


def need_retry(exception: Exception) -> bool:
    """Retries requests on 500 series errors.

    Args:
        exception (Exception): The exception raised.

    Returns:
        bool: True if the request should be retried.
    """
    if isinstance(exception, HTTPStatusError):
        status_code = exception.response.status_code
        return status_code in (
            HttpStatusCode.INTERNAL_SERVER_ERROR,
            HttpStatusCode.BAD_GATEWAY,
            HttpStatusCode.SERVICE_UNAVAILABLE,
            HttpStatusCode.GATEWAY_TIMEOUT,
        )
    return False
