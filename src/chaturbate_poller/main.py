"""Main module for the Chaturbate Poller."""

import argparse
import asyncio
import logging
from contextlib import suppress
from logging.config import dictConfig

from chaturbate_poller import __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.logging_config import LOGGING_CONFIG

# Module-level logger
logger = logging.getLogger(__name__)


def initialize_logging() -> None:  # pragma: no cover
    """Initialize logging and force a log rotation on start."""
    dictConfig(LOGGING_CONFIG)

    # Get the file handler and rotate on start
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.doRollover()  # Force rollover on start


def parse_arguments() -> argparse.Namespace:  # pragma: no cover
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Poll events from Chaturbate.")
    config_manager = ConfigManager()
    parser.add_argument("--version", action="version", version=f"chaturbate_poller {__version__}")
    parser.add_argument("--testbed", action="store_true", help="Use the testbed environment")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for the API requests")
    parser.add_argument(
        "--username",
        type=str,
        default=config_manager.get("CB_USERNAME", ""),
        help="Chaturbate username (default: from environment variable or config file)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=config_manager.get("CB_TOKEN", ""),
        help="Chaturbate token (default: from environment variable or config file)",
    )
    parser.add_argument("--use-database", action="store_true", help="Enable database integration")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


async def start_polling(  # pylint: disable=too-many-arguments  # pragma: no cover  # noqa: PLR0913
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool,
    verbose: bool,
) -> None:
    """Start polling Chaturbate events."""
    if not username or not token:
        logger.error(
            "CB_USERNAME and CB_TOKEN must be provided as arguments or environment variables."
        )
        return

    async with ChaturbateClient(
        username, token, timeout=api_timeout, testbed=testbed, verbose=verbose
    ) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            if response is None:
                break
            for event in response.events:
                await event_handler.handle_event(event)
            url = str(response.next_url)


def main() -> None:  # pragma: no cover
    """Run the main function within an asyncio event loop."""
    args = parse_arguments()

    # Set logging level based on verbosity
    initialize_logging()
    if args.verbose:
        logging.getLogger("chaturbate_poller").setLevel(logging.DEBUG)
    else:
        logging.getLogger("chaturbate_poller").setLevel(logging.INFO)

    event_handler = create_event_handler("database" if args.use_database else "logging")

    logger.info("Starting Chaturbate Poller...")

    with suppress(KeyboardInterrupt):
        asyncio.run(
            start_polling(
                args.username,
                args.token,
                args.timeout,
                event_handler,
                testbed=args.testbed,
                verbose=args.verbose,
            )
        )
