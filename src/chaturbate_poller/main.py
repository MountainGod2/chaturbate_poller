"""Main module for configuring and running the Chaturbate Poller CLI."""

import asyncio
import logging
import textwrap

import rich_click as click
from rich.console import Console
from rich.traceback import install

from chaturbate_poller import __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.exceptions import AuthenticationError, NotFoundError, PollingError
from chaturbate_poller.logging_config import setup_logging
from chaturbate_poller.signal_handler import SignalHandler

install(show_locals=False, width=100)
console = Console()
"""Console: Rich console for printing messages."""


@click.group()
@click.version_option(version=__version__)
def cli() -> None:  # pragma: no cover
    """Manage and run the Chaturbate Poller CLI."""


@cli.command(
    help=textwrap.dedent(
        """
        Start the Chaturbate Poller.

          chaturbate_poller start --username=user1 --token=abc123 --testbed

          chaturbate_poller start -t 15 -d --verbose
        """
    )
)
@click.option(
    "--username",
    default=lambda: ConfigManager().get("CB_USERNAME", ""),
    show_default="(from configuration)",
    help="Your Chaturbate username.",
)
@click.option(
    "--token",
    default=lambda: ConfigManager().get("CB_TOKEN", ""),
    show_default="(from configuration)",
    help="Your Chaturbate API token.",
)
@click.option(
    "--timeout",
    "-t",
    default=10,
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
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def start(  # noqa: PLR0913  # pylint: disable=too-many-arguments  # pragma: no cover
    username: str,
    token: str,
    timeout: int,
    *,
    testbed: bool,
    database: bool,
    verbose: bool,
) -> None:
    """Start the Chaturbate Poller."""
    setup_logging(verbose=verbose)
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


async def main(  # noqa: PLR0913  # pylint: disable=too-many-arguments  # pragma: no cover
    username: str,
    token: str,
    api_timeout: int,
    *,
    testbed: bool,
    use_database: bool,
    verbose: bool,
) -> None:
    """Main logic for starting the Chaturbate Poller.

    This function sets up the application, including logging, signal handling,
    and initiating the polling loop.

    Args:
        username (str): Chaturbate username.
        token (str): API token for authentication.
        api_timeout (int): API request timeout.
        testbed (bool): Enable or disable testbed mode.
        use_database (bool): Enable or disable database integration.
        verbose (bool): Enable verbose logging.
    """
    logger = logging.getLogger(__name__)

    if not username:
        console.print("[bold red]Error:[/bold red] A username is required.")
        return
    if not token:
        console.print("[bold red]Error:[/bold red] An API token is required.")
        return

    if use_database:
        event_handler = create_event_handler("database")
    else:
        event_handler = create_event_handler("logging")

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
        logger.error("%s: %s", exc.__class__.__name__, exc)  # noqa: TRY400
        console.print(f"[bold red]Error:[/bold red] {exc}")
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.debug("Polling stopped by user.")


async def start_polling(  # noqa: PLR0913  # pylint: disable=too-many-arguments  # pragma: no cover
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool,
    verbose: bool,
) -> None:
    """Begin polling Chaturbate events.

    Args:
        username (str): Chaturbate username.
        token (str): API token.
        api_timeout (int): Timeout for API requests.
        event_handler (EventHandler): Handler to process events.
        testbed (bool): Enable or disable testbed mode.
        verbose (bool): Enable verbose logging.
    """
    async with ChaturbateClient(
        username=username,
        token=token,
        timeout=api_timeout,
        testbed=testbed,
        verbose=verbose,
    ) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            if not response:
                break
            for event in response.events:
                await event_handler.handle_event(event)
            url = str(response.next_url)


if __name__ == "__main__":  # pragma: no cover
    cli()
