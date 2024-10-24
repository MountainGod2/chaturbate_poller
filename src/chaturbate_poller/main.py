"""Main module for the Chaturbate Poller."""

import asyncio
import logging
import logging.config
from contextlib import suppress

import rich_click as click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.traceback import install

from chaturbate_poller import __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import create_event_handler
from chaturbate_poller.exceptions import AuthenticationError, NotFoundError, PollingError
from chaturbate_poller.logging_config import setup_logging
from chaturbate_poller.signal_handler import SignalHandler

# Create a rich console for pretty printing
console = Console()
"""Console: The rich console for pretty printing."""

# Install rich tracebacks to make error handling more user-friendly
install(show_locals=True)


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
def main(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
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

    setup_logging()  # Initialize logging

    if verbose:
        handler = logging.getLogger("chaturbate_poller").handlers[0]
        if isinstance(handler, RichHandler):
            handler.setLevel(logging.DEBUG)

    if not username or not token:
        msg = "Missing credentials"
        raise click.UsageError(msg)

    event_handler = create_event_handler("database" if use_database else "logging")

    console.print(f"[bold green]Starting Chaturbate Poller v{__version__}...[/bold green]")

    loop = asyncio.get_event_loop()

    stop_future = loop.create_future()

    signal_handler = SignalHandler(loop, stop_future)
    signal_handler.setup()

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
                    stop_future,
                )
            )
        except (AuthenticationError, NotFoundError, PollingError) as exc:
            console.print(f"[red]Error: {exc}[/red]")
        except asyncio.CancelledError:
            logging.debug("Shutting down gracefully due to cancellation.")
        finally:
            if not loop.is_closed():
                loop.close()


async def start_polling(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username,  # noqa: ANN001
    token,  # noqa: ANN001
    api_timeout,  # noqa: ANN001
    event_handler,  # noqa: ANN001
    testbed,  # noqa: ANN001
    verbose,  # noqa: ANN001
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
                progress.update(task, advance=1)


if __name__ == "__main__":  # pragma: no cover
    main()
