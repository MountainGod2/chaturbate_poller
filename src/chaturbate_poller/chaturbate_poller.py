"""Chaturbate poller module."""

import logging
from logging.config import dictConfig
from types import TracebackType

import httpx
from backoff import constant, expo, on_exception
from backoff._typing import Details

from chaturbate_poller.constants import DEFAULT_BASE_URL, TESTBED_BASE_URL, HttpStatusCode
from chaturbate_poller.influxdb_client import InfluxDBHandler
from chaturbate_poller.logging_config import LOGGING_CONFIG
from chaturbate_poller.models import EventsAPIResponse

dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)
"""Logger for the module."""


def backoff_handler(details: Details) -> None:
    """Handle backoff events.

    Args:
        details (Details): The backoff details.
    """
    wait = details["wait"]
    tries = details["tries"]
    logger.info("Backing off %s seconds after %s tries", int(wait), int(tries))


def giveup_handler(details: Details) -> None:
    """Handle giveup events.

    Args:
        details (Details): The giveup details.
    """
    tries = details.get("tries", 0)
    exception = details.get("exception")

    if exception and hasattr(exception, "response"):
        response = exception.response
        status_code = response.status_code
        try:
            response_dict = response.json()
            status_text = response_dict.get("status", "Unknown error")
        except ValueError:
            status_text = "Error parsing response JSON"
    else:
        status_code = None
        status_text = "No response available"

    logger.error(
        "Giving up after %s tries due to server error code %s: %s",
        int(tries),
        status_code,
        status_text,
    )


class ChaturbateClient:
    """Client for fetching Chaturbate events.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        timeout (Optional[int]): The timeout for the request.
        base_url (Optional[str]): The base URL for the Chaturbate API.

    Raises:
        ValueError: If username or token are not provided.
    """

    def __init__(
        self, username: str, token: str, timeout: int | None = None, *, testbed: bool = False
    ) -> None:
        """Initialize the client."""
        if not username or not token:
            msg = "Chaturbate username and token are required."
            raise ValueError(msg)
        if testbed:
            self.base_url = TESTBED_BASE_URL
        else:
            self.base_url = DEFAULT_BASE_URL
        if timeout is not None and timeout < 0:
            msg = "Timeout must be a positive integer."
            raise ValueError(msg)
        self.timeout = timeout
        self.username = username
        self.token = token
        self._client: httpx.AsyncClient | None = None
        self.influxdb_handler: InfluxDBHandler = InfluxDBHandler()

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
        on_giveup=giveup_handler,
        on_backoff=backoff_handler,
        logger=None,
    )
    @on_exception(
        wait_gen=expo,
        jitter=None,
        base=1.25,
        factor=5,
        exception=httpx.HTTPStatusError,
        giveup=lambda retry: not need_retry(retry),
        on_giveup=giveup_handler,
        max_tries=6,
        on_backoff=backoff_handler,
        logger=None,
        raise_on_giveup=False,
    )
    async def fetch_events(self, url: str | None = None) -> EventsAPIResponse:
        """Fetch events from the Chaturbate API.

        Args:
            url (Optional[str]): The URL to fetch events from.

        Returns:
            EventsAPIResponse: The events API response.

        Raises:
            ValueError: If unauthorized access occurs.
            httpx.HTTPStatusError: For other HTTP errors.
        """
        url = url or self._construct_url()
        logger.debug("%s", url)
        response = await self.client.get(url, timeout=None)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == HttpStatusCode.UNAUTHORIZED:
                msg = "Unauthorized access. Verify the username and token."
                raise ValueError(msg) from e
            raise

        # Validate the response model
        events_api_response = EventsAPIResponse.model_validate(response.json())

        # Write events to InfluxDB
        for event in events_api_response.events:
            self.influxdb_handler.write_event("chaturbate_events", event.model_dump())

        return events_api_response

    def _construct_url(self) -> str:
        """Construct URL with username, token, and timeout.

        Returns:
            str: The constructed URL.
        """
        timeout_param = f"?timeout={self.timeout}" if self.timeout else ""
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"


def need_retry(exception: Exception) -> bool:
    """Determine if the request should be retried based on the exception.

    Args:
        exception (Exception): The exception raised.

    Returns:
        bool: True if the request should be retried, False otherwise.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        if status_code in {
            HttpStatusCode.INTERNAL_SERVER_ERROR,
            HttpStatusCode.BAD_GATEWAY,
            HttpStatusCode.SERVICE_UNAVAILABLE,
            HttpStatusCode.GATEWAY_TIMEOUT,
            HttpStatusCode.WEB_SERVER_IS_DOWN,
        }:
            return True
    return False
