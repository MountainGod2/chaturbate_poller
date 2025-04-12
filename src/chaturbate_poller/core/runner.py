"""Main module for configuring and running the Chaturbate Poller."""

from __future__ import annotations

import asyncio
import logging
import typing

from chaturbate_poller.core.polling import start_polling
from chaturbate_poller.handlers.factory import create_event_handler
from chaturbate_poller.logging.config import setup_logging
from chaturbate_poller.utils.signal_handler import SignalHandler

if typing.TYPE_CHECKING:
    from chaturbate_poller.handlers.event_handler import EventHandler


async def main(  # noqa: PLR0913  # pylint: disable=too-many-arguments
    username: str,
    token: str,
    api_timeout: int = 10,
    *,
    testbed: bool = False,
    use_database: bool = False,
    verbose: bool = False,
) -> None:
    """Main entry point for the Chaturbate Poller.

    Sets up logging, initializes the event handler, and starts polling.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        api_timeout (int, optional): Timeout for API requests in seconds. Defaults to 10.
        testbed (bool, optional): Whether to use the testbed environment. Defaults to False.
        use_database (bool, optional): Whether to use the database for storing events. Defaults to
            False.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.

    Raises:
        ValueError: If username or token are not provided.
    """
    logger: logging.Logger = logging.getLogger(name=__name__)
    setup_logging(verbose=verbose)

    if not username or not token:
        msg = "Username and token are required"
        logger.error(msg)
        raise ValueError(msg)

    event_handler: EventHandler = create_event_handler(
        handler_type="database" if use_database else "logging"
    )
    stop_future: asyncio.Future[None] = asyncio.Future()

    signal_handler: SignalHandler = SignalHandler(
        loop=asyncio.get_running_loop(), stop_future=stop_future
    )
    await signal_handler.setup()

    try:
        await asyncio.gather(
            start_polling(
                username=username,
                token=token,
                api_timeout=api_timeout,
                event_handler=event_handler,
                testbed=testbed,
            ),
            stop_future,
        )
    except asyncio.CancelledError:
        logger.info("Polling stopped by user.")
