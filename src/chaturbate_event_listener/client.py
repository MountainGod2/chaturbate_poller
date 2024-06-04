"""Chaturbate Event Client module."""

import asyncio
import os
import re
from collections.abc import Callable
from types import TracebackType
from typing import Any

import backoff
from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    ServerDisconnectedError,
)
from dotenv import load_dotenv

from chaturbate_event_listener.errors import (
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from chaturbate_event_listener.event_handler import EventHandler
from chaturbate_event_listener.logger import logger

load_dotenv()


class ChaturbateEventClient:
    """Chaturbate Event Client class."""

    def __init__(  # noqa: PLR0913
        self,
        username: str | None = os.getenv("CHATURBATE_USERNAME", ""),
        token: str | None = os.getenv("CHATURBATE_TOKEN", ""),
        timeout: int = 20,
        url: str | None = None,
        event_handler: Callable[[dict[str, Any]], None] | None = None,
        *,
        is_testbed: bool = False,
    ) -> None:
        """Initialize ChaturbateEventClient instance.

        Args:
            username (str): Chaturbate username.
            token (str): Chaturbate API token.
            timeout (int): Request timeout in seconds.
            url (str, optional): Base URL for fetching events.
            event_handler (Callable[[dict[str, Any]], None], optional): Event handler
                function.
            is_testbed (bool, optional): Flag to use testbed URL.
        """
        self.base_url = (
            url or f"https://events.testbed.cb.dev/events/{username}/{token}/"
            if is_testbed
            else f"https://eventsapi.chaturbate.com/events/{username}/{token}/"
        )
        self.timeout: int = timeout
        self.event_handler: Callable = event_handler or EventHandler()
        self.session: ClientSession | None = None
        logger.debug("ChaturbateEventClient initialized")

    async def __aenter__(self) -> "ChaturbateEventClient":
        """Start the client session."""
        self.session = ClientSession(
            timeout=ClientTimeout(total=(self.timeout + 10)), raise_for_status=True
        )
        logger.debug("ClientSession started")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()
            logger.debug("ClientSession closed")
            self.session = None

    @staticmethod
    def is_fatal_error(exception: Exception) -> bool:
        """Check if the exception is fatal.

        Args:
            exception (Exception): Exception instance.

        Returns:
            bool: True if the exception is fatal, False otherwise.
        """
        if isinstance(exception, ClientResponseError):
            if exception.status in {401, 403, 404}:
                return True
            if 500 <= exception.status < 600:  # noqa: PLR2004
                return False
        return True

    @backoff.on_exception(
        backoff.constant,
        (ClientResponseError),
        jitter=None,
        interval=20,
        max_tries=3,
        giveup=is_fatal_error,
        on_backoff=lambda details: logger.warning(
            f"Retrying in {details['wait']:.1f} seconds"
        ),
        on_giveup=lambda details: logger.error(
            f"Giving up after {details['tries']} tries"
        ),
        raise_on_giveup=True,
    )
    async def retrieve_events(self, url: str) -> dict[str, Any]:
        """Retrieve events from the given URL.

        Args:
            url (str): URL to fetch events from.

        Returns:
            dict[str, Any]: Events data.

        Raises:
            TimeoutError: If request times out.
            UnauthorizedError: If unauthorized access.
            ForbiddenError: If forbidden access.
            NotFoundError: If resource not found.
        """
        if not self.session:
            msg = "Client session is not initialized"
            logger.error(msg)
            raise RuntimeError(msg)

        http_request_timeout = ClientTimeout(total=self.timeout + 10)
        semaphore = asyncio.Semaphore(10)
        try:
            async with (
                semaphore,
                self.session.get(url, timeout=http_request_timeout) as response,
            ):
                logger.debug(
                    f"Successfully fetched events from {self._sanitize_url(url)}"
                )
                return await response.json()
        except TimeoutError:
            logger.error(f"Request to {self._sanitize_url(url)} timed out")
            raise
        finally:
            logger.debug("Request completed")

    async def process_events(self, url: str | None = None) -> None:
        """Process events from the given URL.

        Args:
            url (str, optional): URL to fetch events from.

        Raises:
            UnauthorizedError: If unauthorized access.
            ForbiddenError: If forbidden access.
            NotFoundError: If resource not found.
        """
        logger.info("Event processing started")
        url = url or f"{self.base_url}?timeout={self.timeout}"
        try:
            while url:
                events_data = await self.retrieve_events(url)
                for message in events_data.get("events", []):
                    self.event_handler(message)
                url = events_data.get("nextUrl")
                if url:
                    logger.debug(f"Fetching next URL: {self._sanitize_url(url)}")
                else:
                    logger.debug("No more events")
            logger.debug("Stopping event processing")
        except ClientResponseError as error:
            if error.status == 401:  # noqa: PLR2004
                msg = "Unauthorized access"
                raise UnauthorizedError(msg) from error
            if error.status == 403:  # noqa: PLR2004
                msg = "Forbidden access"
                raise ForbiddenError(msg) from error
            if error.status == 404:  # noqa: PLR2004
                msg = "Resource not found"
                raise NotFoundError(msg) from error
        except ServerDisconnectedError as error:
            logger.error(f"Server disconnected: {error}")
            raise
        except asyncio.CancelledError:
            logger.info("Event processing was cancelled")
        finally:
            await self.__aexit__(None, None, None)
            logger.info("Event processing completed")

    def _sanitize_url(self, url: str) -> str:
        patterns = [
            r"(?<=/events/)[^/]+(?=/)",
            r"(?<=/)[a-zA-Z0-9]{20,}(?=/)",
            r"(?<=\?i=)[a-zA-Z0-9-]+(?=&)",
        ]

        for pattern in patterns:
            url = re.sub(pattern, "*****", url)

        return url
