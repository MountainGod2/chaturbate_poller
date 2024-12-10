"""Main module for configuring and running the Chaturbate Poller CLI.

This script provides a command-line interface (CLI) for setting up and running
the Chaturbate Poller. It includes commands for interactive setup, starting
the poller, and handling various configurations and options.
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

# Enable detailed and formatted error handling with Rich
install(show_locals=False, width=100)

# Set up a Rich console for consistent and styled CLI output
console = Console(width=100)


@click.group()
@click.version_option(version=__version__)
def cli() -> None:  # pragma: no cover
    """Manage and run the Chaturbate Poller CLI."""


@cli.command()
def setup() -> None:  # pragma: no cover
    """Interactive setup to generate the .env file.

    This command guides the user through configuring the application by
    prompting for essential credentials and optional database settings.
    """
    console.print("[bold green]Chaturbate Poller Setup[/bold green]")
    console.print("This setup will help you configure the necessary settings.")

    # Prompt user for essential settings
    cb_username = Prompt.ask("Enter your Chaturbate username")
    cb_token = Prompt.ask("Enter your Chaturbate API token", password=True)
    use_influxdb = Confirm.ask("Would you like to configure InfluxDB?", default=False)

    # Gather configurations into a dictionary
    config = {"CB_USERNAME": cb_username, "CB_TOKEN": cb_token}

    # Add InfluxDB configurations if enabled
    if use_influxdb:
        config.update(_get_influxdb_config())

    # Save the configuration to an .env file
    _save_env_file(config)


def _get_influxdb_config() -> dict[str, str]:  # pragma: no cover
    """Prompt for InfluxDB configuration details.

    Returns:
        dict[str, str]: A dictionary containing InfluxDB connection details.
    """
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
    """Save the provided configuration to a .env file.

    Args:
        config (dict[str, str]): Key-value pairs to write to the .env file.

    This function ensures existing configurations are not overwritten without user confirmation.
    """
    env_file_path = Path(".env")
    if env_file_path.exists() and not Confirm.ask(
        f"{env_file_path} already exists. Overwrite?", default=False
    ):
        console.print("[yellow]Setup aborted. Existing configuration preserved.[/yellow]")
        return

    try:
        with env_file_path.open("w", encoding="utf-8") as file:
            # Write each configuration key-value pair to the file
            file.writelines(f'{key}="{value}"\n' for key, value in config.items())
        console.print(f"[bold green]Configuration saved to {env_file_path}[/bold green]")
    except OSError as exc:
        # Catch file writing errors and display an appropriate message
        console.print(f"[red]Error saving configuration: {exc}[/red]")


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
def start(  # pylint: disable=too-many-arguments,too-many-positional-arguments  # noqa: PLR0913  # pragma: no cover
    username: str, token: str, timeout: int, *, testbed: bool, database: bool, verbose: bool
) -> None:
    """Start the Chaturbate Poller.

    This command initializes the application and runs the main async polling loop.
    """
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


async def main(  # pylint: disable=too-many-arguments  # noqa: PLR0913  # pragma: no cover
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
    setup_logging(verbose=verbose)
    _validate_inputs(username, token)

    # Determine the appropriate event handler
    event_handler = create_event_handler("database" if use_database else "logging")
    console.print(f"[bold green]Starting Chaturbate Poller v{__version__}...[/bold green]")

    stop_future: asyncio.Future[None] = asyncio.Future()

    # Set up signal handling for graceful shutdown
    signal_handler = SignalHandler(asyncio.get_running_loop(), stop_future)
    await signal_handler.setup()

    try:
        # Run the polling coroutine alongside a stop signal
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
    except AuthenticationError as exc:
        console.print(f"[red]Authentication Error: {exc}[/red]")
    except NotFoundError as exc:
        console.print(f"[red]Not Found Error: {exc}[/red]")
    except PollingError as exc:
        console.print(f"[red]Polling Error: {exc}[/red]")
    except (asyncio.CancelledError, KeyboardInterrupt):
        console.print("[yellow]Polling stopped by user request.[/yellow]")


def _validate_inputs(username: str, token: str) -> None:  # pragma: no cover
    """Validate mandatory inputs for running the poller.

    Args:
        username (str): Chaturbate username.
        token (str): API token.

    Raises:
        click.BadParameter: If required inputs are missing.
    """
    if not username:
        msg = "A username is required."
        raise click.BadParameter(msg)
    if not token:
        msg = "An API token is required."
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
    """Begin polling Chaturbate events with feedback.

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
        total_events = 0  # Track the total number of processed events
        url = None  # Initialize the URL for event polling

        # Use a rich progress spinner to provide user feedback
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Polling events...", total=None)

            while True:
                try:
                    # Fetch events from the API
                    response = await client.fetch_events(url)
                    if not response:
                        break

                    # Process each event and increment the counter
                    for event in response.events:
                        total_events += 1
                        await event_handler.handle_event(event)

                    # Update the URL for the next fetch cycle
                    url = str(response.next_url)

                    # Update progress feedback
                    progress.update(
                        task,
                        description=f"[green]{total_events} events processed.",
                    )
                except Exception as exc:
                    # Log and re-raise errors encountered during polling
                    progress.update(task, description=f"[red]Error: {exc}[/red]")
                    raise


if __name__ == "__main__":  # pragma: no cover
    cli()
