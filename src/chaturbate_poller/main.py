"""Main module for the Chaturbate Poller."""

import asyncio
import logging
import logging.handlers
from contextlib import suppress
from logging.config import dictConfig

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.traceback import install

from chaturbate_poller import __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.logging_config import LOGGING_CONFIG
from chaturbate_poller.signal_handler import SignalHandler

# Module-level logger and console for Rich
logger = logging.getLogger(__name__)
console = Console()

# Install rich tracebacks to make error handling more user-friendly
install(show_locals=True)


def initialize_logging() -> None:  # pragma: no cover
    """Initialize logging using the logging configuration."""
    dictConfig(LOGGING_CONFIG)


@click.command()
@click.option("--version", is_flag=True, help="Show the version and exit.")
@click.option("--testbed", is_flag=True, help="Use the testbed environment.")
@click.option("--timeout", default=10, help="Timeout for the API requests.")
@click.option(
    "--username",
    default=lambda: ConfigManager().get("CB_USERNAME", ""),
    help="Chaturbate username.",
)
@click.option(
    "--token", default=lambda: ConfigManager().get("CB_TOKEN", ""), help="Chaturbate token."
)
@click.option("--use-database", is_flag=True, help="Enable database integration.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(  # pylint: disable=too-many-arguments, too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    version,  # noqa: ANN001
    testbed,  # noqa: ANN001
    timeout,  # noqa: ANN001
    username,  # noqa: ANN001
    token,  # noqa: ANN001
    use_database,  # noqa: ANN001
    verbose,  # noqa: ANN001
) -> None:
    """Run the Chaturbate Poller."""
    if version:
        console.print(f"chaturbate_poller [bold green]v{__version__}[/bold green]")
        return

    initialize_logging()

    # Set log level based on verbosity
    if verbose:
        logging.getLogger("chaturbate_poller").setLevel(logging.DEBUG)
    else:
        logging.getLogger("chaturbate_poller").setLevel(logging.INFO)

    if not username or not token:
        msg = "Missing credentials"
        raise click.UsageError(msg)

    event_handler = create_event_handler("database" if use_database else "logging")

    console.print(f"[bold green]Starting Chaturbate Poller v{__version__}...[/bold green]")

    # Create the asyncio event loop
    loop = asyncio.get_event_loop()

    # Future to stop the event loop on signal
    stop_future = loop.create_future()

    # Instantiate the signal handler and setup signals
    signal_handler = SignalHandler(loop, stop_future)
    signal_handler.setup()

    # Use asyncio.run to run the polling loop and wait for the stop signal
    with suppress(KeyboardInterrupt):
        try:
            loop.run_until_complete(
                asyncio.gather(
                    start_polling(
                        username=username,
                        token=token,
                        api_timeout=timeout,
                        event_handler=event_handler,
                        testbed=testbed,
                        verbose=verbose,
                    ),
                    stop_future,  # Ensure that we wait for the signal to stop
                )
            )
        except PollingError as exc:
            logger.error(exc)  # noqa: TRY400
        except asyncio.CancelledError:
            logger.debug("Shutting down gracefully due to cancellation.")
        finally:
            if not loop.is_closed():
                loop.close()


async def start_polling(  # pylint: disable=too-many-arguments  # noqa: PLR0913  # pragma: no cover
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool,
    verbose: bool,
) -> None:
    """Start polling Chaturbate events."""
    async with ChaturbateClient(
        username, token, timeout=api_timeout, testbed=testbed, verbose=verbose
    ) as client:
        url = None
        with Progress(
            SpinnerColumn(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[green]Polling Chaturbate...", total=100)
            while not progress.finished:
                response = await client.fetch_events(url)
                if response is None:
                    break
                for event in response.events:
                    await event_handler.handle_event(event)
                url = str(response.next_url)
                progress.update(task, advance=1)  # Update the progress bar


if __name__ == "__main__":  # pragma: no cover
    main()
