"""Chaturbate poller module."""

from __future__ import annotations

import logging
import typing

import backoff
import httpx

from chaturbate_poller.config.backoff import backoff_config
from chaturbate_poller.constants import (
    DEFAULT_BASE_URL,
    HTTP_CLIENT_TIMEOUT,
    TESTBED_BASE_URL,
    HttpStatusCode,
)
from chaturbate_poller.database.influxdb_handler import InfluxDBHandler
from chaturbate_poller.exceptions import (
    AuthenticationError,
    NotFoundError,
)
from chaturbate_poller.logging.config import sanitize_sensitive_data
from chaturbate_poller.models.api_response import EventsAPIResponse
from chaturbate_poller.utils import helpers
from chaturbate_poller.utils.error_handler import handle_giveup, log_backoff

if typing.TYPE_CHECKING:
    import types

logger = logging.getLogger(__name__)


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
        """Initialize the client.

        Raises:
            ValueError: If username or token are not provided, or timeout is invalid.
        """
        if not username or not token:
            msg = "Chaturbate username and token are required."
            logger.error(msg)
            raise ValueError(msg)

        if timeout is not None and timeout < 0:
            msg = "Timeout must be a non-negative integer."
            logger.error(msg)
            raise ValueError(msg)

        self.base_url: str = TESTBED_BASE_URL if testbed else DEFAULT_BASE_URL
        self.timeout: int | None = timeout
        self.username: str = username
        self.token: str = token
        self.influxdb_handler: InfluxDBHandler = InfluxDBHandler()

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> typing.Self:
        """Initialize the async client."""
        self._client = httpx.AsyncClient(timeout=HTTP_CLIENT_TIMEOUT)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit the asynchronous context manager.

        Args:
            exc_type (type[BaseException] | None): Exception type, if raised.
            exc_value (BaseException | None): Exception value, if raised.
            traceback (types.TracebackType | None): Exception traceback, if raised.
        """
        if self._client:
            await self._client.aclose()
        self._client = None

    @backoff.on_exception(
        wait_gen=backoff.constant,
        interval=backoff_config.get_constant_interval,
        jitter=None,
        exception=httpx.ReadError,
        max_tries=backoff_config.get_read_error_max_tries,
        on_giveup=handle_giveup,
        on_backoff=log_backoff,
        logger=None,
    )
    @backoff.on_exception(
        wait_gen=backoff.expo,
        jitter=None,
        base=backoff_config.get_base,
        factor=backoff_config.get_factor,
        exception=httpx.HTTPStatusError,
        giveup=lambda retry: not helpers.need_retry(exception=retry),
        on_giveup=handle_giveup,
        max_tries=backoff_config.get_max_tries,
        on_backoff=log_backoff,
        logger=None,
        raise_on_giveup=False,
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from the Chaturbate API.

        Args:
            url (str | None): Optional URL to fetch events from. If None, constructs a URL from
                configuration.

        Returns:
            EventsAPIResponse: The API response containing events.

        Raises:
            AuthenticationError: If authentication fails.
            NotFoundError: If the resource is not found.
            TimeoutError: If a timeout occurs while fetching events.
            HTTPStatusError: If any other HTTP status error occurs.
        """
        if self._client is None:
            msg = "Client has not been initialized. Use 'async with ChaturbateClient()'."
            raise RuntimeError(msg)

        fetch_url: str = url or self._construct_url()
        logger.debug("Fetching events from URL: %s", sanitize_sensitive_data(arg=fetch_url))

        try:
            response: httpx.Response = await self._client.get(url=fetch_url, timeout=None)
            response.raise_for_status()
            logger.debug(
                "Successfully fetched events from: %s", sanitize_sensitive_data(arg=fetch_url)
            )
        except httpx.HTTPStatusError as http_err:
            status_code: int = http_err.response.status_code
            logger.warning(
                "HTTPStatusError: %s occurred while fetching events from URL: %s",
                status_code,
                sanitize_sensitive_data(arg=fetch_url),
            )

            if status_code == HttpStatusCode.UNAUTHORIZED:
                msg = "Invalid authentication credentials."
                raise AuthenticationError(message=msg) from http_err
            if status_code == HttpStatusCode.NOT_FOUND:
                msg = "Resource not found at the requested URL."
                raise NotFoundError(message=msg) from http_err
            raise
        except httpx.TimeoutException as timeout_err:
            logger.exception(
                "Timeout occurred while fetching events from URL: %s",
                sanitize_sensitive_data(arg=fetch_url),
            )
            msg = "Timeout while fetching events."
            raise TimeoutError(msg) from timeout_err

        return EventsAPIResponse.model_validate(obj=response.json())

    def _construct_url(self) -> str:
        """Construct the URL for fetching events.

        Returns:
            str: The constructed URL including timeout parameters.
        """
        timeout_param: str = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"
