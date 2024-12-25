"""Main module for configuring and running the Chaturbate Poller."""

import asyncio
import logging

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.exceptions import AuthenticationError, NotFoundError, PollingError
from chaturbate_poller.logging_config import setup_logging
from chaturbate_poller.signal_handler import SignalHandler


async def start_polling(  # noqa: PLR0913
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool = False,
    verbose: bool = False,
) -> None:
    """Begin polling Chaturbate events."""
    async with ChaturbateClient(
        username=username,
        token=token,
        timeout=api_timeout,
        testbed=testbed,
        verbose=verbose,
    ) as client:
        next_url: str | None = None
        while True:
            response = await client.fetch_events(next_url)
            if not response or not response.events:
                break
            for event in response.events:
                await event_handler.handle_event(event)
            if not response.next_url:
                break
            next_url = response.next_url


async def main(  # noqa: PLR0913
    username: str,
    token: str,
    api_timeout: int = 10,
    *,
    testbed: bool = False,
    use_database: bool = False,
    verbose: bool = False,
) -> None:
    """Main application entry point."""
    logger = logging.getLogger(__name__)
    setup_logging(verbose=verbose)

    if not username or not token:
        msg = "Username and token are required"
        logger.error(msg)
        raise ValueError(msg)

    event_handler = create_event_handler("database" if use_database else "logging")
    stop_future: asyncio.Future[None] = asyncio.Future()

    signal_handler = SignalHandler(asyncio.get_running_loop(), stop_future)
    await signal_handler.setup()

    try:
        await asyncio.gather(
            start_polling(
                username=username,
                token=token,
                api_timeout=api_timeout,
                event_handler=event_handler,
                testbed=testbed,
                verbose=verbose,
            ),
            stop_future,
        )
    except (AuthenticationError, NotFoundError, PollingError) as exc:
        logger.error("Polling error: %s", exc)  # noqa: TRY400
        raise
    except asyncio.CancelledError:  # pragma: no cover
        logger.debug("Polling stopped by user.")
