"""Chaturbate poller module."""

import logging
from types import TracebackType

import httpx
from backoff import constant, expo, on_exception

from chaturbate_poller.constants import (
    DEFAULT_BASE_URL,
    TESTBED_BASE_URL,
    HttpStatusCode,
)
from chaturbate_poller.exceptions import (
    AuthenticationError,
    NotFoundError,
)
from chaturbate_poller.influxdb_handler import InfluxDBHandler
from chaturbate_poller.logging_config import sanitize_sensitive_data
from chaturbate_poller.models import EventsAPIResponse
from chaturbate_poller.utils import ChaturbateUtils

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        timeout (int | None): Timeout for API requests in seconds.
        testbed (bool): Whether to use the testbed environment.

    Raises:
        ValueError: If username or token are not provided, or timeout is invalid.
    """

    def __init__(
        self, username: str, token: str, timeout: int | None = None, *, testbed: bool = False
    ) -> None:
        """Initialize the client."""
        if not username or not token:
            msg = "Chaturbate username and token are required."
            logger.error(msg)
            raise ValueError(msg)

        if timeout is not None and timeout < 0:
            msg = "Timeout must be a positive integer."
            logger.error(msg)
            raise ValueError(msg)

        self.base_url = TESTBED_BASE_URL if testbed else DEFAULT_BASE_URL
        self.timeout = timeout
        self.username = username
        self.token = token
        self._client: httpx.AsyncClient | None = None
        self.influxdb_handler = InfluxDBHandler()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or initialize the HTTP client.

        Returns:
            httpx.AsyncClient: The initialized HTTP client.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=300)
        return self._client

    async def __aenter__(self) -> "ChaturbateClient":
        """Enter an asynchronous context manager.

        Returns:
            ChaturbateClient: The current instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the asynchronous context manager.

        Args:
            exc_type (type[BaseException] | None): Exception type, if raised.
            exc_value (BaseException | None): Exception value, if raised.
            traceback (TracebackType | None): Exception traceback, if raised.
        """
        await self.client.aclose()
        self.influxdb_handler.close()

    @on_exception(
        wait_gen=constant,
        interval=2,
        jitter=None,
        exception=httpx.ReadError,
        max_tries=10,
        on_giveup=ChaturbateUtils.giveup_handler,
        on_backoff=ChaturbateUtils.backoff_handler,
        logger=None,
    )
    @on_exception(
        wait_gen=expo,
        jitter=None,
        base=1.25,
        factor=5,
        exception=httpx.HTTPStatusError,
        giveup=lambda retry: not ChaturbateUtils.need_retry(retry),
        on_giveup=ChaturbateUtils.giveup_handler,
        max_tries=ChaturbateUtils.get_max_tries,
        on_backoff=ChaturbateUtils.backoff_handler,
        logger=None,
        raise_on_giveup=False,
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from the Chaturbate API.

        Args:
            url (str | None): Optional URL to fetch events from. If None, constructs a URL from
                configuration.

        Returns:
            EventsAPIResponse: The parsed response containing events and the next URL.

        Raises:
            AuthenticationError: If authentication fails.
            NotFoundError: If the requested resource is not found.
            PollingError: For other unrecoverable polling errors.
            TimeoutError: If a timeout occurs during the request.
        """
        url = url or self._construct_url()
        logger.debug("Fetching events from URL: %s", sanitize_sensitive_data(url))

        try:
            response = await self.client.get(url, timeout=None)
            response.raise_for_status()
            logger.info("Successfully fetched events from: %s", sanitize_sensitive_data(url))
        except httpx.HTTPStatusError as http_err:
            status_code = http_err.response.status_code
            logger.warning(
                "HTTPStatusError: %s occurred while fetching events from URL: %s",
                status_code,
                sanitize_sensitive_data(url),
            )

            if status_code == HttpStatusCode.UNAUTHORIZED:
                msg = "Invalid authentication credentials."
                raise AuthenticationError(msg) from http_err
            if status_code == HttpStatusCode.NOT_FOUND:
                msg = "Resource not found at the requested URL."
                raise NotFoundError(msg) from http_err
            raise
        except httpx.TimeoutException as timeout_err:
            logger.exception(
                "Timeout occurred while fetching events from URL: %s", sanitize_sensitive_data(url)
            )
            msg = "Timeout while fetching events."
            raise TimeoutError(msg) from timeout_err

        return EventsAPIResponse.model_validate(response.json())

    def _construct_url(self) -> str:
        """Construct the URL for fetching events.

        Returns:
            str: The constructed URL including timeout parameters.
        """
        timeout_param = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"
