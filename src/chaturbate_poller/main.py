"""Main module for the Chaturbate Poller CLI.

This module provides a feature-rich CLI for configuring and running the Chaturbate Poller.
"""

import asyncio
import textwrap
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt
from rich.traceback import install

from chaturbate_poller import __version__
from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.event_handler import EventHandler, create_event_handler
from chaturbate_poller.exceptions import AuthenticationError, NotFoundError, PollingError
from chaturbate_poller.logging_config import setup_logging
from chaturbate_poller.signal_handler import SignalHandler

# Enable rich traceback
install(show_locals=True)

# Setup rich console
console = Console(width=100)

# Click styling configuration
click.rich_click.STYLE_ARGUMENT = "cyan"
click.rich_click.STYLE_COMMAND = "bold"
click.rich_click.STYLE_HELPTEXT = "dim"
click.rich_click.STYLE_OPTION = "green"
click.rich_click.STYLE_OPTION_DEFAULT = "dim"
click.rich_click.STYLE_OPTION_HELP = "cyan"


@click.group()
@click.version_option(version=__version__)
def cli() -> None:  # pragma: no cover
    """Manage and run the Chaturbate Poller."""


@cli.command()
def setup() -> None:  # pragma: no cover
    """Interactive setup to generate the .env file."""
    console.print("[bold green]Chaturbate Poller Setup[/bold green]")
    console.print("This setup will help you configure the necessary settings.")

    # Prompt for basic configuration
    cb_username = Prompt.ask("Enter your Chaturbate username")
    cb_token = Prompt.ask("Enter your Chaturbate API token", password=True)
    use_influxdb = Confirm.ask("Would you like to configure InfluxDB?", default=False)

    config = {"CB_USERNAME": cb_username, "CB_TOKEN": cb_token}

    if use_influxdb:
        config.update(_get_influxdb_config())

    _save_env_file(config)


def _get_influxdb_config() -> dict[str, str]:  # pragma: no cover
    """Prompt for InfluxDB configuration."""
    console.print("\n[bold cyan]InfluxDB Configuration[/bold cyan]")
    influxdb_url = Prompt.ask("Enter your InfluxDB URL", default="http://localhost:8086")
    influxdb_token = Prompt.ask("Enter your InfluxDB token", password=True)
    influxdb_org = Prompt.ask("Enter your InfluxDB organization")
    influxdb_bucket = Prompt.ask("Enter your InfluxDB bucket")

    return {
        "INFLUXDB_URL": influxdb_url,
        "INFLUXDB_TOKEN": influxdb_token,
        "INFLUXDB_ORG": influxdb_org,
        "INFLUXDB_BUCKET": influxdb_bucket,
        "USE_DATABASE": "true",
    }


def _save_env_file(config: dict[str, str]) -> None:  # pragma: no cover
    """Save configuration to the .env file."""
    env_file_path = Path(".env")
    if env_file_path.exists() and not Confirm.ask(
        f"{env_file_path} already exists. Overwrite?", default=False
    ):
        console.print("[yellow]Setup aborted. Existing configuration preserved.[/yellow]")
        return

    try:
        with env_file_path.open("w", encoding="utf-8") as file:
            file.writelines(f'{key}="{value}"\n' for key, value in config.items())
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
def start(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username: str, token: str, timeout: int, *, testbed: bool, database: bool, verbose: bool
) -> None:
    """Start the Chaturbate Poller."""
    asyncio.run(
        main(
            username=username,
            token=token,
            timeout=timeout,
            testbed=testbed,
            use_database=database,
            verbose=verbose,
        )
    )


async def main(  # pylint: disable=too-many-arguments  # noqa: PLR0913  # pragma: no cover
    username: str,
    token: str,
    timeout: int,  # noqa: ASYNC109
    *,
    testbed: bool,
    use_database: bool,
    verbose: bool,
) -> None:
    """Main logic for starting the Chaturbate Poller."""
    setup_logging(verbose=verbose)
    _validate_inputs(username, token)

    event_handler = create_event_handler("database" if use_database else "logging")
    console.print(f"[bold green]Starting Chaturbate Poller v{__version__}...[/bold green]")

    stop_future: asyncio.Future[None] = asyncio.Future()

    signal_handler = SignalHandler(asyncio.get_running_loop(), stop_future)
    await signal_handler.setup()

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
    except AuthenticationError as exc:
        console.print(f"[red]Authentication Error: {exc}[/red]")
        console.print(
            "[yellow]Ensure your token has the correct permissions or enable testbed mode.[/yellow]"
        )
    except NotFoundError as exc:
        console.print(f"[red]Not Found Error: {exc}[/red]")
        console.print("[yellow]Ensure your username is correct and the resource exists.[/yellow]")
    except PollingError as exc:
        console.print(f"[red]Polling Error: {exc}[/red]")
    except (asyncio.CancelledError, KeyboardInterrupt):
        console.print("[yellow]Polling stopped by user request.[/yellow]")


def _validate_inputs(username: str, token: str) -> None:  # pragma: no cover
    """Ensure mandatory inputs are provided."""
    if not username:
        msg = "A username is required. Use --username or set it in the .env file."
        raise click.BadParameter(msg)
    if not token:
        msg = "An API token is required. Use --token or set it in the .env file."
        raise click.BadParameter(msg)


async def start_polling(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool,
    verbose: bool,
) -> None:
    """Begin polling Chaturbate events with feedback."""
    async with ChaturbateClient(
        username=username,
        token=token,
        timeout=api_timeout,
        testbed=testbed,
        verbose=verbose,
    ) as client:
        total_events = 0
        url = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Polling Chaturbate events...", total=None)

            while True:
                try:
                    response = await client.fetch_events(url)
                    if not response:
                        break

                    for event in response.events:
                        total_events += 1
                        await event_handler.handle_event(event)

                    url = str(response.next_url)
                    progress.update(
                        task,
                        description=f"[green]{len(response.events)} events processed this request, "
                        f"{total_events} events processed in total.",
                    )
                except Exception as exc:
                    progress.update(task, description=f"[red]Error: {exc}[/red]")
                    raise


if __name__ == "__main__":  # pragma: no cover
    cli()
