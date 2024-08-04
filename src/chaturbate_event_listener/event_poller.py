"""Event poller module.

This module contains the EventPoller class responsible for polling events.
"""

import asyncio
import logging
import signal
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import aiohttp
import orjson
from rich.console import Console
from tenacity import (
    RetryError,
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from chaturbate_event_listener.config import (
    SERVER_ERROR_STATUS_CODE_THRESHOLD,
    UNAUTHORIZED_ERROR,
    Config,
)
from chaturbate_event_listener.errors import ServerError, UnauthorizedError
from chaturbate_event_listener.event_store import EventStore, get_event_store
from chaturbate_event_listener.models import Event


class EventPoller:
    """Event poller class.

    Attributes:
        config (Config): The configuration.
        session_factory (Callable[[], aiohttp.ClientSession]): Factory function to create aiohttp
            client session.
        url (str): The URL to poll for events.
        logger (logging.Logger): The logger.
        console (Console): The rich console.
        event_callbacks (dict[str, list[Callable[[Event], None]]): A dictionary of event callbacks.
    """

    def __init__(
        self,
        config: Config,
        session_factory: Callable[[], aiohttp.ClientSession] = aiohttp.ClientSession,
    ) -> None:
        """Initialize the EventPoller.

        Args:
            config (Config): The configuration.
            session_factory (Callable[[], aiohttp.ClientSession], optional): Factory function to
                create aiohttp client session. Defaults to aiohttp.ClientSession.
        """
        self.config = config
        self.url = config.url
        self.session_factory = session_factory
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.event_callbacks: dict[str, list[Callable[[Event], None]]] = {}
        self.event_store: EventStore = get_event_store(config)

    def register_callback(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Register an event callback.

        Args:
            event_type (str): The event type.
            callback (Callable[[Event], None]): The callback function.
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)

    async def poll(self) -> None:
        """Poll for events."""
        try:
            async with self.get_client_session() as session:
                while True:
                    events, next_url = await self.get_events(session, self.url)
                    for event in events:
                        self._handle_event(event)
                    if not next_url:
                        self.logger.warning("No nextUrl found, stopping polling.")
                        break
                    self.url = next_url
        except RetryError as e:
            self.logger.exception("Max retries reached, stopping polling.", exc_info=e)
        except UnauthorizedError:
            self.logger.exception("Unauthorized error: check your username and token.")
        except asyncio.CancelledError:
            self.logger.debug("Polling cancelled.")

    def _handle_event(self, event: Event) -> None:
        if event.method in self.event_callbacks:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.console.log(event.to_json())
            for callback in self.event_callbacks[event.method]:
                callback(event)
        self.event_store.store_event(event)

    @retry(
        after=after_log(logging.getLogger(__name__), log_level=logging.DEBUG),
        stop=stop_after_attempt(20),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(ServerError),
    )
    async def get_events(
        self, session: aiohttp.ClientSession, url: str
    ) -> tuple[list[Event], str | None]:
        """Get events from the URL.

        Args:
            session (aiohttp.ClientSession): The aiohttp client session.
            url (str): The URL to get events from.

        Returns:
            tuple[list[Event], str | None]: A tuple of events and the next URL.
        """
        self.logger.debug("Fetching events from: %s", url)
        async with session.get(url) as response:
            if response.status >= SERVER_ERROR_STATUS_CODE_THRESHOLD:
                msg = f"Server error: {response.status}"
                raise ServerError(msg)
            if response.status == UNAUTHORIZED_ERROR:
                msg = "Unauthorized error."
                raise UnauthorizedError(msg)
            response.raise_for_status()
            data = await response.json(loads=orjson.loads)
            events = data.get("events", [])
            next_url = data.get("nextUrl")
            parsed_events = [Event.from_dict(event) for event in events if self._parse_event(event)]
            return parsed_events, next_url

    @staticmethod
    def _parse_event(event: dict) -> Event | None:
        try:
            parsed_event = Event.from_dict(event)
        except KeyError:
            return None
        return parsed_event if parsed_event else None

    @asynccontextmanager
    async def get_client_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        """Get an aiohttp client session."""
        async with self.session_factory() as session:
            yield session

    async def shutdown(self, loop: asyncio.AbstractEventLoop) -> None:
        """Shutdown the event poller.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
        """
        self.logger.debug("Received exit signal, shutting down...")
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        self.logger.debug("Cancelling %s outstanding tasks", len(tasks))
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
        raise asyncio.CancelledError

    def run(self) -> None:
        """Run the event poller."""
        self.logger.info("Starting event poller...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown(loop)))
        try:
            loop.run_until_complete(self.poll())
        except asyncio.CancelledError:
            self.logger.debug("Event poller cancelled.")
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
