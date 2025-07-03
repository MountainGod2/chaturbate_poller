"""Main module for configuring and running the Chaturbate Poller."""

from __future__ import annotations

import asyncio
import logging
import typing

from chaturbate_poller.config.backoff import BackoffConfig
from chaturbate_poller.core.polling import start_polling
from chaturbate_poller.exceptions import AuthenticationError
from chaturbate_poller.handlers.factory import create_event_handler
from chaturbate_poller.logging.config import setup_logging
from chaturbate_poller.utils.signal_handler import SignalHandler

if typing.TYPE_CHECKING:
    from chaturbate_poller.handlers.event_handler import EventHandler
    from chaturbate_poller.models.options import PollerOptions


async def main(options: PollerOptions) -> None:
    """Main entry point for the Chaturbate Poller.

    Sets up logging, initializes the event handler, and starts polling.

    Args:
        options (PollerOptions): Configuration options for the poller.

    Raises:
        AuthenticationError: If username or token are not provided.
    """
    await run_with_options(options)


async def run_with_options(options: PollerOptions) -> None:
    """Run the poller with the given options.

    Args:
        options (PollerOptions): Configuration options for the poller.

    Raises:
        AuthenticationError: If username or token are not provided.
    """
    logger: logging.Logger = logging.getLogger(name=__name__)
    setup_logging(verbose=options.verbose)

    if not options.username or not options.token:
        msg = "Username and token are required."
        logger.error(msg)
        raise AuthenticationError(msg)

    event_handler: EventHandler = create_event_handler(
        handler_type="database" if options.use_database else "logging"
    )
    stop_future: asyncio.Future[None] = asyncio.Future()

    signal_handler: SignalHandler = SignalHandler(
        loop=asyncio.get_running_loop(), stop_future=stop_future
    )

    signal_handler.setup()

    # Create backoff configuration instance
    backoff_config = BackoffConfig()

    await asyncio.gather(
        start_polling(
            username=options.username,
            token=options.token,
            api_timeout=options.timeout,
            event_handler=event_handler,
            testbed=options.testbed,
            backoff_config=backoff_config,
        ),
        stop_future,
    )

    signal_handler.cleanup()
