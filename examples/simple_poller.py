"""Simple example demonstrating basic usage of the Chaturbate Poller.

Features event formatting, unified configuration, and error handling.
"""

import asyncio
import contextlib
from typing import TYPE_CHECKING

from rich.console import Console
from rich.json import JSON

from chaturbate_poller import ChaturbateClient, ConfigManager, format_message

if TYPE_CHECKING:
    from chaturbate_poller.models.event import Event

console = Console()


def handle_event(event: "Event") -> None:
    """Handle events with formatting."""
    formatted_message = format_message(event)

    if formatted_message:
        console.print(formatted_message)
    else:
        console.print(f"Raw event ({event.method}):")
        console.print(JSON(event.model_dump_json(exclude_none=True)))


async def poll_events(client: "ChaturbateClient") -> None:
    """Continuously poll for events."""
    url = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                handle_event(event)
            url = response.next_url

    except asyncio.CancelledError:
        console.print("Polling stopped by user")
    except Exception as e:
        console.print(f"Error occurred: {e}")
        raise


async def main() -> None:
    """Basic usage example."""
    config = ConfigManager()
    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    if not username or not token:
        console.print("Please set CB_USERNAME and CB_TOKEN in your environment.")
        console.print("You can create a .env file or export them as environment variables.")
        return

    async with ChaturbateClient(username, token, testbed=True) as client:
        console.print("Starting event polling...")
        console.print("Using testbed environment")
        console.print("Press Ctrl+C to stop")
        await poll_events(client)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
