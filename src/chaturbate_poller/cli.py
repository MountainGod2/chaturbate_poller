"""Command-line interface for the Chaturbate Poller."""

import asyncio

import rich_click as click
from rich.console import Console
from rich.traceback import install

from chaturbate_poller import __version__
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.main import main

console = Console()
install(console=console)


@click.group()
@click.version_option(version=__version__, prog_name="chaturbate-poller")
def cli() -> None:
    """Manage and run the Chaturbate Poller CLI."""


@cli.command()
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
def start(  # noqa: PLR0913
    username: str,
    token: str,
    timeout: int,
    *,
    testbed: bool,
    database: bool,
    verbose: bool,
) -> None:
    """Start the Chaturbate Poller."""
    if not username or not token:
        console.print("[red]Error: Chaturbate username and token are required.[/red]")
        raise SystemExit(1)
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


if __name__ == "__main__":  # pragma: no cover
    cli()