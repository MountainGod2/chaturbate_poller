import asyncio
import contextlib
from typing import TYPE_CHECKING

from rich.console import Console
from rich.json import JSON

from chaturbate_poller import ChaturbateClient, ConfigManager

if TYPE_CHECKING:
    from chaturbate_poller.models.event import Event

console = Console()


def handle_event(event: "Event") -> None:
    """Example event handler function."""
    # You can process events however you want
    # This example just prints them as JSON
    console.print(JSON(event.model_dump_json(exclude_none=True)))


async def poll_events(client: "ChaturbateClient") -> None:
    """Demonstrate continuous event polling."""
    # When URL is None, the client will format the initial request URL using the base URL and
    # provided username/token
    url = None

    try:
        while True:
            # Fetch new events from the Chaturbate API
            response = await client.fetch_events(url)

            # Process each event in the response object using the handler function
            for event in response.events:
                handle_event(event)

            # Get URL for next poll request
            url = response.next_url

    except asyncio.CancelledError:
        # Stop polling if cancelled. (E.g. by pressing Ctrl+C)
        pass


async def main() -> None:
    """Example showing basic usage of the Chaturbate poller."""
    # Load config from environment variables
    config = ConfigManager()
    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    # Check if username and token are set
    if not username or not token:
        console.print("Please set CB_USERNAME and CB_TOKEN in your environment.")
        return

    # Create client instance using context manager
    async with ChaturbateClient(username, token, testbed=True) as client:
        # Start polling and run until cancelled
        console.print("Starting event polling...")
        await poll_events(client)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
