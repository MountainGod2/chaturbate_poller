"""Application runner with configuration and event handling setup."""

from __future__ import annotations

import typing

from chaturbate_poller.config.backoff import BackoffConfig
from chaturbate_poller.core.polling import start_polling
from chaturbate_poller.handlers.factory import HandlerType, create_event_handler
from chaturbate_poller.logging.config import setup_logging

if typing.TYPE_CHECKING:
    from chaturbate_poller.handlers.event_handler import EventHandler
    from chaturbate_poller.models.options import PollerOptions


async def main(options: PollerOptions) -> None:
    """Configure and start the Chaturbate poller.

    Sets up logging, creates event handler, and begins polling.

    Args:
        options: Poller configuration options.
    """
    setup_logging(verbose=options.verbose)

    event_handler: EventHandler = create_event_handler(
        handler_type=HandlerType.DATABASE if options.use_database else HandlerType.LOGGING
    )

    # Create backoff configuration instance
    backoff_config = BackoffConfig()

    await start_polling(
        username=options.username,
        token=options.token,
        api_timeout=options.timeout,
        event_handler=event_handler,
        testbed=options.testbed,
        backoff_config=backoff_config,
    )
