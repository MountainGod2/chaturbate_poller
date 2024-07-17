"""Event poller module."""

import asyncio
import logging
import signal
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import aiohttp
import orjson
from rich.console import Console
from rich.progress import Progress, SpinnerColumn
from rich.table import Table
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
from chaturbate_event_listener.models import Event


class EventPoller:
    """Polls events from the Chaturbate API.

    Attributes:
        config (Config): The configuration object.
        url (str): The API URL.
        session_factory (Callable[[], aiohttp.ClientSession]): The aiohttp session factory.
        logger (logging.Logger): The logger.
        console (Console): The rich console.
        event_callbacks (dict[str, list[Callable[[Event], None]]]): The event callbacks.
    """

    def __init__(
        self,
        config: Config,
        session_factory: Callable[[], aiohttp.ClientSession] = aiohttp.ClientSession,
    ) -> None:
        """Initialize the event poller.

        Args:
            config (Config): The configuration object.
            session_factory (Callable[[], aiohttp.ClientSession], optional): The aiohttp session
                factory. Defaults to aiohttp.ClientSession.
        """
        self.config = config
        self.url = config.url
        self.session_factory = session_factory
        self.logger = logging.getLogger(__name__)
        self.console = Console()
        self.event_callbacks: dict[str, list[Callable[[Event], None]]] = {}

    def register_callback(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Register a callback function for a specific event type.

        Args:
            event_type (str): The type of event to register the callback for.
            callback (Callable[[Event], None]): The callback function.
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)

    async def poll(self) -> None:
        """Poll events from the API."""
        try:
            async with self.get_client_session() as session:
                with Progress(
                    SpinnerColumn(), transient=True, expand=True, console=self.console
                ) as progress:
                    task = progress.add_task("Polling events...", total=None)
                    while True:
                        progress.start_task(task)
                        events, next_url = await self.get_events(session, self.url)
                        progress.update(task, advance=1)

                        for event in events:
                            self._handle_event(event)

                        if not next_url:
                            self.logger.warning("No nextUrl found, stopping polling.")
                            break

                        self.url = next_url
        except RetryError as e:
            self.logger.exception("Max retries reached, stopping polling.", exc_info=e)
        except UnauthorizedError:
            self.logger.error("Unauthorized error: check your username and token.")  # noqa: TRY400

    def _handle_event(self, event: Event) -> None:
        """Handle an event by calling registered callbacks.

        Args:
            event (Event): The event object.
        """
        if event.method in self.event_callbacks:
            for callback in self.event_callbacks[event.method]:
                callback(event)

        table = Table(title="Event Details")
        table.add_column("Key", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        for key, value in event.object.__dict__.items():
            table.add_row(key, str(value))

        self.console.print(table)

    @retry(
        after=after_log(
            logger=logging.getLogger(__name__),
            log_level=logging.DEBUG,
            sec_format="%0.0f",
        ),
        stop=stop_after_attempt(20),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(ServerError),
    )
    async def get_events(
        self, session: aiohttp.ClientSession, url: str
    ) -> tuple[list[Event], str | None]:
        """Fetch events from the API.

        Args:
            session (aiohttp.ClientSession): The aiohttp session.
            url (str): The API URL.

        Returns:
            tuple[list[Event], Optional[str]]: A tuple containing a list of
            events and the next URL.
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

    def _format_tip_message(self, event: Event) -> str:
        """Format the tip event message.

        Args:
            event (Event): The event object.

        Returns:
            str: The formatted tip event message.
        """
        if not event.object.tip or not event.object.user:
            return "Invalid tip event received."

        tip_message = (
            event.object.tip.message.removeprefix(" | ") if event.object.tip.message else None
        )

        if event.object.tip.is_anon:
            return (
                f"An anonymous user tipped {event.object.tip.tokens} tokens "
                f"with message: '{tip_message}'"
                if tip_message
                else f"An anonymous user tipped {event.object.tip.tokens} tokens."
            )

        return (
            f"User {event.object.user.username} tipped {event.object.tip.tokens} tokens "
            f"with message: '{tip_message}'"
            if tip_message
            else f"User {event.object.user.username} tipped {event.object.tip.tokens} tokens."
        )

    @staticmethod
    def _parse_event(event: dict) -> Event | None:
        """Parse an event from the event dictionary.

        Args:
            event (dict): The event dictionary.

        Returns:
            Optional[Event]: The parsed event or None if parsing fails.
        """
        try:
            parsed_event = Event.from_dict(event)
        except KeyError:
            return None
        else:
            return parsed_event if parsed_event else None

    @asynccontextmanager
    async def get_client_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        """Get an aiohttp client session.

        Yields:
            AsyncIterator[aiohttp.ClientSession]: The aiohttp client session.
        """
        async with self.session_factory() as session:
            yield session

    def _get_event_message(self, event: Event) -> str | None:
        """Get the formatted event message based on event method.

        Args:
            event (Event): The event object.

        Returns:
            Optional[str]: The formatted event message or None if no matching method.
        """
        method_to_message = {
            "broadcastStart": lambda e: f"Broadcast started by {e.object.broadcaster}.",
            "broadcastStop": lambda e: f"Broadcast stopped by {e.object.broadcaster}.",
            "userEnter": lambda e: f"User {e.object.user.username} entered the room.",
            "userLeave": lambda e: f"User {e.object.user.username} left the room.",
            "follow": lambda e: f"User {e.object.user.username} followed the broadcaster.",
            "unfollow": lambda e: f"User {e.object.user.username} unfollowed the broadcaster.",
            "chatMessage": lambda e: (
                f"Chat message from {e.object.user.username}: " f"'{e.object.message.message}'"
            ),
            "fanclubJoin": lambda e: f"User {e.object.user.username} joined the fan club.",
            "mediaPurchase": lambda e: (
                f"User {e.object.user.username} purchased {e.object.media.type} set "
                f"{e.object.media.name} for {e.object.media.tokens} tokens."
            ),
            "privateMessage": lambda e: (
                f"Private message from {e.object.message.from_user} to "
                f"{e.object.message.to_user}: '{e.object.message.message}'"
            ),
            "roomSubjectChange": lambda e: f"Room subject changed to: '{e.object.subject}'",
            "tip": self._format_tip_message,
        }

        format_message = method_to_message.get(event.method)
        return format_message(event) if format_message else None

    async def shutdown(self, loop: asyncio.AbstractEventLoop) -> None:
        """Shutdown the event poller.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.

        Raises:
            asyncio.CancelledError: If the event poller is cancelled.
        """
        self.logger.debug("Received exit signal, shutting down...")
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        self.logger.debug("Cancelling %d outstanding tasks", len(tasks))
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
        raise asyncio.CancelledError

    def run(self) -> None:
        """Start the event poller."""
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
