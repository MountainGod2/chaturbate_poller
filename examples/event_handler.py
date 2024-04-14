"""Example of fetching Chaturbate events and printing only large tips."""  # noqa: INP001

import asyncio
import os

import chaturbate_poller
from dotenv import load_dotenv

LARGE_TIP_THRESHOLD = 100

load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


async def tip_handler(tip) -> None:  # noqa: ANN001
    """Print a message for large tips.

    Args:
        tip (Tip): The tip event.
    """
    if tip.tokens >= LARGE_TIP_THRESHOLD:
        print(f"Large tip of {tip.tokens} tokens!")  # noqa: T201


async def main() -> None:
    """Example of fetching Chaturbate events and printing only large tips."""
    async with chaturbate_poller.ChaturbateClient(
        username, token, base_url=chaturbate_poller.constants.TESTBED_BASE_URL
    ) as client:
        url = None  # Ensure url starts as None or a valid URL string

        while True:  # Loop indefinitely
            response = await client.fetch_events(url=url)  # Fetch events from the API
            for event in response.events:  # Handle each event in the response
                # Check if the event is a tip event
                if event.method == "tip":
                    tip = event.object.tip
                    # Handle the tip event
                    await tip_handler(tip)

            # Update the URL for the next request
            url = str(response.next_url)


if __name__ == "__main__":
    # Run the main coroutine using asyncio
    asyncio.run(main())
