# pylint: disable=C0103,E1125,E1120
"""The main module for the Chaturbate event listener.

This module provides a command-line interface for starting the event poller.

Example:
    $ python -m chaturbate_event_listener --username testuser --token testtoken
"""

import os

import click
from dotenv import load_dotenv
from rich_click import RichCommand

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller
from chaturbate_event_listener.logging_config import setup_logging

load_dotenv()


@click.command(cls=RichCommand)
@click.option(
    "--username",
    default=lambda: os.environ.get("CHATURBATE_USERNAME"),
    help="Your Chaturbate username.",
    required=True,
)
@click.option(
    "--token",
    default=lambda: os.environ.get("CHATURBATE_TOKEN"),
    help="Your Chaturbate API token.",
    required=True,
)
@click.option(
    "--timeout",
    default=lambda: int(os.environ.get("CHATURBATE_TIMEOUT", 10)),
    help="The timeout for the API request.",
    type=int,
)
@click.option("--testbed", is_flag=True, help="Use the testbed URL.")
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def start(username: str, token: str, timeout: int, *, testbed: bool, debug: bool) -> None:
    """Start the event poller.

    Args:
        username (str): Your Chaturbate username.
        token (str): Your Chaturbate API token.
        timeout (int): The timeout for the API request.
        testbed (bool): Whether to use the testbed URL.
        debug (bool): Whether to enable debug logging.
    """
    setup_logging(debug=debug)

    # Validate username and token
    if not username:
        msg = "Username cannot be empty."
        raise click.BadParameter(msg)
    if not token:
        msg = "Token cannot be empty."
        raise click.BadParameter(msg)

    config = Config(username=username, token=token, timeout=timeout, use_testbed=testbed)
    poller = EventPoller(config)
    poller.run()


if __name__ == "__main__":
    start()
