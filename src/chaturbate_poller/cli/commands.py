"""CLI commands for the Chaturbate Poller."""

from __future__ import annotations

import asyncio
import logging
import sys

import rich_click as click

from chaturbate_poller import __version__
from chaturbate_poller.config.manager import ConfigManager
from chaturbate_poller.constants import API_TIMEOUT
from chaturbate_poller.core.runner import main
from chaturbate_poller.exceptions import PollingError

logger: logging.Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


@click.group()
@click.version_option(version=__version__, prog_name="chaturbate-poller")
def cli() -> None:
    """Manage and run the Chaturbate Poller CLI."""


@cli.command()
@click.option(
    "--username",
    default=lambda: ConfigManager().get(key="CB_USERNAME", default=""),
    show_default="(from configuration)",
    help="Your Chaturbate username.",
)
@click.option(
    "--token",
    default=lambda: ConfigManager().get(key="CB_TOKEN", default=""),
    show_default="(from configuration)",
    help="Your Chaturbate API token.",
)
@click.option(
    "--timeout",
    "-t",
    default=API_TIMEOUT,
    show_default=True,
    help="Timeout for API requests, in seconds.",
)
@click.option(
    "--database/--no-database",
    "-d/-n",
    default=False,
    show_default=True,
    help="Enable or disable database integration.",
)
@click.option("--testbed", is_flag=True, help="Enable testbed mode.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def start(  # noqa: PLR0913  # pylint: disable=too-many-arguments
    username: str,
    token: str,
    timeout: int,
    *,
    testbed: bool,
    database: bool,
    verbose: bool,
) -> None:
    """Start the Chaturbate Poller."""
    try:
        asyncio.run(
            main(
                username=username,
                token=token,
                api_timeout=timeout,
                testbed=testbed,
                use_database=database,
                verbose=verbose,
            )
        )
    except PollingError:
        logger.exception("Polling error encountered. Exiting.")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    cli()
