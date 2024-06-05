"""Entry point for running the package as a script.

This module provides the command-line interface for the package.
"""

import asyncio
import contextlib
import logging
import os

import click
from dotenv import load_dotenv

from chaturbate_event_listener import __version__
from chaturbate_event_listener.client import ChaturbateEventClient
from chaturbate_event_listener.logger import logger

load_dotenv()


@click.command()
@click.argument(
    "username", required=True, default=lambda: os.getenv("CHATURBATE_USERNAME", "")
)
@click.argument(
    "token", required=True, default=lambda: os.getenv("CHATURBATE_TOKEN", "")
)
@click.option(
    "--timeout", default=10, help="Timeout for the event feed (default is 10 seconds)."
)
@click.option("--use-testbed", is_flag=True, help="Use the Chaturbate testbed API.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging output.")
@click.option(
    "--log-file",
    default="chaturbate_event_listener.log",
    help="Log file path (default is 'chaturbate_event_listener.log').",
)
@click.version_option(prog_name="chaturbate-event-listener", version=__version__)
@click.help_option()
def cli_main(  # noqa: PLR0913
    username: str,
    token: str,
    timeout: int,
    *,
    use_testbed: bool,
    verbose: bool,
    log_file: str,
) -> None:
    """Poll the Chaturbate API for events."""
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Enabling verbose logging.")

    file_handler = logging.FileHandler(log_file)
    logger.addHandler(file_handler)

    try:
        logger.debug("Starting asyncio.run")
        asyncio.run(run(username, token, timeout, use_testbed=use_testbed))
    finally:
        logger.debug("Exiting main")


async def run(username: str, token: str, timeout: int, *, use_testbed: bool) -> None:
    """Run the event listener."""
    async with ChaturbateEventClient(
        username, token, timeout, is_testbed=use_testbed
    ) as chaturbate_events:
        with contextlib.suppress(KeyboardInterrupt, asyncio.CancelledError):
            await chaturbate_events.process_events()
