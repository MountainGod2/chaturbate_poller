import asyncio
import contextlib

from rich.console import Console
from rich.json import JSON

from chaturbate_poller import ChaturbateClient, ConfigManager

console = Console()


def handle_event(event) -> None:
    """Example event handler function."""
    # You can process events however you want
    # This example just prints them as JSON
    console.print(JSON(event.model_dump_json(exclude_none=True)))


async def poll_events(client: ChaturbateClient) -> None:
    """Demonstrate continuous event polling."""
    url = None  # Initial URL is None for first request

    try:
        while True:
            # Fetch new events - this handles pagination automatically
            response = await client.fetch_events(url)

            # Process each event in the response
            for event in response.events:
                handle_event(event)

            # Get URL for next poll request
            url = response.next_url

    except asyncio.CancelledError:
        # Clean shutdown on cancellation
        pass


async def main() -> None:
    """Example showing basic usage of the Chaturbate poller."""
    # Load config from environment variables
    config = ConfigManager()
    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    # Create client instance using context manager
    async with ChaturbateClient(username, token, testbed=True) as client:
        # Start polling - runs until cancelled
        console.print("Starting event polling...")
        await poll_events(client)


# Run the example
if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
