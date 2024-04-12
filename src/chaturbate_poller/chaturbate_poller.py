"""Chaturbate poller module."""

import logging
from logging.config import dictConfig
from types import TracebackType

import backoff
import httpx

from chaturbate_poller.constants import DEFAULT_BASE_URL, HttpStatusCode
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
        """Initialize the Chaturbate client.

        Args:
            username (str): The Chaturbate username.
            token (str): The Chaturbate token.
            timeout (int, optional): The timeout for the API request. Defaults to None.
            base_url (str, optional): The URL for fetching events. Defaults to None.

        Raises:
            ValueError: If the username or token is not provided.
        """
        if not username or not token:
            msg = "Chaturbate username and token are required."
            raise ValueError(msg)

        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.username = username
        self.token = token
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client.

        Returns:
            httpx.AsyncClient: The HTTP client.
        """
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client

    async def __aenter__(self) -> "ChaturbateClient":
        """Enter client."""
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
        (httpx.HTTPStatusError, httpx.HTTPStatusError, httpx.ReadError),
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
        logger=logger,
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
                msg = "Unauthorized access. Verify the username and token."
                raise ValueError(msg) from e
            raise
        return EventsAPIResponse.model_validate(response.json())

    def _construct_url(self) -> str:
        """Construct URL with username, token, and timeout.

        Returns:
            str: The constructed URL.
        """
        timeout_param = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"  # noqa: E501


def need_retry(exception: Exception) -> bool:
    """Retries requests on 500 series errors.

    Args:
        exception (Exception): The exception raised.

    Returns:
        bool: True if the request should be retried.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        if status_code in (
            HttpStatusCode.INTERNAL_SERVER_ERROR,
            HttpStatusCode.BAD_GATEWAY,
            HttpStatusCode.SERVICE_UNAVAILABLE,
            HttpStatusCode.GATEWAY_TIMEOUT,
            HttpStatusCode.WEB_SERVER_IS_DOWN,
        ):
            return True

    if isinstance(exception, httpx.ReadError):
        return True
    return False
