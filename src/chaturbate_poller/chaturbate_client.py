"""Chaturbate poller module."""

import logging
from types import TracebackType

import httpx
from backoff import constant, expo, on_exception

from chaturbate_poller.constants import DEFAULT_BASE_URL, TESTBED_BASE_URL, HttpStatusCode
from chaturbate_poller.influxdb_client import InfluxDBHandler
from chaturbate_poller.models import EventsAPIResponse
from chaturbate_poller.utils import ChaturbateUtils


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
        self.logger = logging.getLogger(__name__)

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
        on_giveup=ChaturbateUtils().giveup_handler,
        on_backoff=ChaturbateUtils().backoff_handler,
        logger=None,
    )
    @on_exception(
        wait_gen=expo,
        jitter=None,
        base=1.25,
        factor=5,
        exception=httpx.HTTPStatusError,
        giveup=lambda retry: not ChaturbateUtils().need_retry(retry),
        on_giveup=ChaturbateUtils().giveup_handler,
        max_tries=6,
        on_backoff=ChaturbateUtils().backoff_handler,
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
        self.logger.debug("%s", url)
        response = await self.client.get(url, timeout=None)
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
        return f"{self.base_url.format(username=self.username, token=self.token)}{timeout_param}"
