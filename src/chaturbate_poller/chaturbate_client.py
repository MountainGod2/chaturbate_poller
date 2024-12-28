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
from chaturbate_poller.logging_config import (
    sanitize_sensitive_data,
)
from chaturbate_poller.models import EventsAPIResponse
from chaturbate_poller.utils import ChaturbateUtils

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        timeout (int): The API timeout.
        logger (logging.Logger): The logger instance.
        testbed (bool): Whether to use the testbed environment.
        verbose (bool): Whether to enable verbose logging.

    Raises:
        ValueError: If username or token are not provided.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        username: str,
        token: str,
        timeout: int | None = None,
        *,
        testbed: bool = False,
    ) -> None:
        """Initialize the client."""
        if not username or not token:
            logger.error("Initialization failed: Chaturbate username and token are required.")
            msg = "Chaturbate username and token are required."
            raise ValueError(msg)
        if timeout is not None and timeout < 0:
            msg = "Timeout must be a positive integer."
            raise ValueError(msg)
        if testbed:
            self.base_url = TESTBED_BASE_URL
            logger.debug("Using testbed environment.")
        else:
            self.base_url = DEFAULT_BASE_URL
        self.timeout = timeout
        self.username = username
        self.token = token
        self._client: httpx.AsyncClient | None = None
        self.influxdb_handler: InfluxDBHandler = InfluxDBHandler()
        self.max_tries = ChaturbateUtils.get_max_tries()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client.

        Returns:
            httpx.AsyncClient: The HTTP client.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=300)
        return self._client

    async def __aenter__(self) -> "ChaturbateClient":
        """Enter client context.

        Returns:
            ChaturbateClient: The client instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit client context."""
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
            url (str): The URL to fetch events from.

        Returns:
            EventsAPIResponse: The events API response.

        Raises:
            AuthenticationError: If the request fails due to invalid authentication.
            NotFoundError: If the requested resource is not found.
            PollingError: For general polling errors.
        """
        url = url or self._construct_url()
        logger.debug("Fetching events from URL: %s", sanitize_sensitive_data(url))

        try:
            response = await self.client.get(url, timeout=None)
            response.raise_for_status()
            logger.debug("Successfully fetched events from: %s", sanitize_sensitive_data(url))
        except httpx.HTTPStatusError as http_err:
            status_code = http_err.response.status_code
            logger.warning("HTTPStatusError occurred with status code: %s", status_code)

            if status_code == HttpStatusCode.UNAUTHORIZED:
                raise AuthenticationError from http_err
            if status_code == HttpStatusCode.NOT_FOUND:
                raise NotFoundError from http_err
            raise
        except httpx.TimeoutException as timeout_err:
            logger.exception("Timeout occurred while fetching events.")
            msg = "Timeout occurred while fetching events."
            raise TimeoutError(msg) from timeout_err

        return EventsAPIResponse.model_validate(response.json())

    def _construct_url(self) -> str:
        """Construct URL with username, token, and timeout.

        Returns:
            str: The constructed URL.
        """
        timeout_param = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"
