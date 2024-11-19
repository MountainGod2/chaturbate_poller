"""Main module for the Chaturbate Poller.

This module provides a CLI interface for setting up and running the Chaturbate Poller.
It includes commands for configuration setup and starting the polling process.
"""

import asyncio
import logging
import logging.config
import textwrap
from contextlib import suppress
from pathlib import Path

import rich_click as click
from rich import traceback
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt

from chaturbate_poller import __author__, __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.exceptions import PollingError
from chaturbate_poller.logging_config import setup_logging
from chaturbate_poller.signal_handler import SignalHandler

console = Console(width=100)
"""Console: The rich console for pretty printing."""

traceback.install(show_locals=True)

click.rich_click.STYLE_ARGUMENT = "cyan"
click.rich_click.STYLE_COMMAND = "bold"
click.rich_click.STYLE_HELPTEXT = "dim"
click.rich_click.STYLE_OPTION = "green"
click.rich_click.STYLE_OPTION_DEFAULT = "dim"
click.rich_click.STYLE_OPTION_HELP = "cyan"


@click.group()
@click.version_option(version=__version__, message=f"%(prog)s v%(version)s by {__author__}")
def cli() -> None:  # pragma: no cover
    """Chaturbate Poller CLI."""


@cli.command()
def setup() -> None:  # pragma: no cover
    """Interactive setup to generate the .env file."""
    console.print("[bold green]Welcome to the Chaturbate Poller Setup[/bold green]\n")
    console.print("This setup will help you generate the required configuration settings.")
    console.print("Press [bold]Ctrl+C[/bold] at any time to cancel.\n")

    cb_username = Prompt.ask("Enter your Chaturbate username")
    cb_token = Prompt.ask("Enter your Chaturbate API token", password=True)

    use_influxdb = Confirm.ask("Do you want to configure InfluxDB settings?", default=False)

    config = {
        "CB_USERNAME": cb_username,
        "CB_TOKEN": cb_token,
    }

    if use_influxdb:
        influxdb_url = Prompt.ask("Enter your InfluxDB URL", default="http://localhost:8086")
        influxdb_token = Prompt.ask("Enter your InfluxDB token", password=True)
        influxdb_org = Prompt.ask("Enter your InfluxDB organization")
        influxdb_bucket = Prompt.ask("Enter your InfluxDB bucket")

        config.update({
            "INFLUXDB_URL": influxdb_url,
            "INFLUXDB_TOKEN": influxdb_token,
            "INFLUXDB_ORG": influxdb_org,
            "INFLUXDB_BUCKET": influxdb_bucket,
            "USE_DATABASE": "true",
        })

    env_file_path = Path(".env")
    if env_file_path.exists():
        overwrite = Confirm.ask(
            f"{env_file_path} already exists. Do you want to overwrite it?", default=False
        )
        if not overwrite:
            console.print("[yellow]Setup cancelled. Existing configuration preserved.[/yellow]")
            return

    try:
        with env_file_path.open("w", encoding="utf-8") as env_file:
            for key, value in config.items():
                env_file.write(f'{key}="{value}"\n')
        console.print(f"[bold green]Configuration saved to {env_file_path}[/bold green]")
    except OSError as exc:
        console.print(f"[red]Error saving configuration: {exc}[/red]")


@cli.command(
    help=textwrap.dedent(
        """
        Start the Chaturbate Poller.

        Examples:

            chaturbate_poller start --username=user1 --token=abc123 --testbed

            chaturbate_poller start --verbose --use-database --timeout=5
        """
    )
)
@click.option(
    "--username",
    default=lambda: ConfigManager().get("CB_USERNAME", ""),
    help="Chaturbate username.",
)
@click.option(
    "--token", default=lambda: ConfigManager().get("CB_TOKEN", ""), help="Chaturbate token."
)
@click.option("--timeout", default=10, help="Timeout for the API requests.", show_default=True)
@click.option("--testbed", is_flag=True, help="Use the testbed environment.")
@click.option("--use-database", is_flag=True, help="Enable database integration.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.version_option(version=__version__, message=f"%(prog)s v%(version)s by {__author__}")
def start(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username: str,
    token: str,
    timeout: int,
    *,
    testbed: bool,
    use_database: bool,
    verbose: bool,
) -> None:  # pragma: no cover
    """CLI entrypoint for Chaturbate Poller."""
    asyncio.run(
        main(
            testbed=testbed,
            timeout=timeout,
            username=username,
            token=token,
            use_database=use_database,
            verbose=verbose,
        )
    )


async def main(  # pylint: disable=too-many-arguments  # noqa: PLR0913
    timeout: int,  # noqa: ASYNC109
    username: str,
    token: str,
    *,
    testbed: bool,
    use_database: bool,
    verbose: bool,
) -> None:  # pragma: no cover
    """Main entrypoint for the Chaturbate Poller."""
    setup_logging()

    if verbose:
        handler = logging.getLogger("chaturbate_poller").handlers[0]
        if isinstance(handler, RichHandler):
            handler.setLevel(logging.DEBUG)

    if not username:
        msg = "Username is required. Use --username or set it in the .env file."
        raise click.BadParameter(msg)

    if not token:
        msg = "Token is required. Use --token or set it in the .env file."
        raise click.BadParameter(msg)

    event_handler = create_event_handler("database" if use_database else "logging")

    console.print(f"[bold green]Starting Chaturbate Poller v{__version__}...[/bold green]")

    stop_future: asyncio.Future[None] = asyncio.Future()

    signal_handler = SignalHandler(asyncio.get_running_loop(), stop_future)
    await signal_handler.setup()

    with suppress(KeyboardInterrupt):
        try:
            await asyncio.gather(
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
        except PollingError as exc:
            console.print(f"[red]Error: {exc}[/red]")
        except asyncio.CancelledError:
            logging.debug("Shutting down gracefully due to cancellation.")


async def start_polling(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool,
    verbose: bool,
) -> None:
    """Start polling Chaturbate events with a progress indicator."""
    async with ChaturbateClient(
        username, token, timeout=api_timeout, testbed=testbed, verbose=verbose
    ) as client:
        url = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Polling Chaturbate events...", total=None)

            event_count = 0

            while True:
                try:
                    response = await client.fetch_events(url)
                    if not response:
                        break

                    for event in response.events:
                        event_count += 1
                        await event_handler.handle_event(event)

                    url = str(response.next_url)

                    progress.update(
                        task,
                        description=f"[green]Processed {len(response.events)} events this request, "
                        f"{event_count} events total processed this run.",
                    )

                except Exception as exc:
                    progress.update(task, description=f"[red]Error: {exc}")
                    raise


if __name__ == "__main__":  # pragma: no cover
    cli()
