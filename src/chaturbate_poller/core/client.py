"""Chaturbate API client."""

from __future__ import annotations

import logging
import typing

import backoff
import httpx

from chaturbate_poller.config.backoff import BackoffConfig
from chaturbate_poller.constants import (
    DEFAULT_BASE_URL,
    HTTP_CLIENT_TIMEOUT,
    TESTBED_BASE_URL,
    HttpStatusCode,
)
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
    from collections.abc import Awaitable, Callable


logger = logging.getLogger(__name__)


class ChaturbateClient:
    """Async HTTP client for Chaturbate Events API.

    Args:
        username: Chaturbate username.
        token: Chaturbate API token.
        timeout: Request timeout in seconds.
        testbed: Use testbed environment.
        backoff_config: Retry configuration.

    Raises:
        ValueError: If credentials are missing or timeout is invalid.
    """

    def __init__(
        self,
        username: str,
        token: str,
        timeout: int | None = None,
        *,
        testbed: bool = False,
        backoff_config: BackoffConfig | None = None,
    ) -> None:
        """Initialize client with credentials and configuration.

        Raises:
            ValueError: If credentials are missing or timeout is invalid.
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
        self.backoff_config: BackoffConfig = backoff_config or BackoffConfig()

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> typing.Self:
        """Enter async context and initialize HTTP client."""
        self._client = httpx.AsyncClient(timeout=HTTP_CLIENT_TIMEOUT)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit async context and cleanup HTTP client.

        Args:
            exc_type: Exception type if raised.
            exc_value: Exception value if raised.
            traceback: Exception traceback if raised.
        """
        if self._client:
            await self._client.aclose()
        self._client = None

    def _create_read_error_backoff(
        self,
    ) -> Callable[
        [Callable[..., Awaitable[EventsAPIResponse]]],
        Callable[..., Awaitable[EventsAPIResponse]],
    ]:
        """Create backoff decorator for network read errors."""
        return backoff.on_exception(
            wait_gen=backoff.constant,
            interval=self.backoff_config.constant_interval,
            jitter=None,
            exception=httpx.ReadError,
            max_tries=self.backoff_config.read_error_max_tries,
            on_giveup=handle_giveup,
            on_backoff=log_backoff,
            logger=None,
        )

    def _create_http_error_backoff(
        self,
    ) -> Callable[
        [Callable[..., Awaitable[EventsAPIResponse]]],
        Callable[..., Awaitable[EventsAPIResponse]],
    ]:
        """Create backoff decorator for HTTP status errors."""
        return backoff.on_exception(
            wait_gen=backoff.expo,
            jitter=None,
            base=self.backoff_config.base,
            factor=self.backoff_config.factor,
            exception=httpx.HTTPStatusError,
            giveup=lambda retry: not helpers.need_retry(exception=retry),
            on_giveup=handle_giveup,
            max_tries=self.backoff_config.max_tries,
            on_backoff=log_backoff,
            logger=None,
            raise_on_giveup=False,
        )

    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from Chaturbate API with retry logic.

        Args:
            url: Custom URL or None to use default endpoint.

        Returns:
            API response containing events and pagination info.

        Raises:
            AuthenticationError: Invalid credentials.
            NotFoundError: Resource not found.
            TimeoutError: Request timeout.
            HTTPStatusError: Other HTTP errors.
        """

        # Apply decorators to the actual fetch method
        @self._create_read_error_backoff()
        @self._create_http_error_backoff()
        async def _do_fetch(fetch_url: str) -> EventsAPIResponse:
            if self._client is None:
                msg = "Client has not been initialized. Use 'async with ChaturbateClient()'."
                raise RuntimeError(msg)

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
            except TypeError as type_err:
                logger.exception(
                    "TypeError occurred while fetching events from URL: %s",
                    sanitize_sensitive_data(arg=fetch_url),
                )
                msg = "Type error while processing the response."
                raise RuntimeError(msg) from type_err
            return EventsAPIResponse.model_validate(obj=response.json())

        fetch_url: str = url or self._construct_url()
        return await _do_fetch(fetch_url)

    def _construct_url(self) -> str:
        """Construct API endpoint URL with optional timeout parameter.

        Returns:
            Complete URL for events endpoint.
        """
        timeout_param: str = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"
