"""Example of using the Chaturbate Poller to fetch events."""

import asyncio
import logging
from contextlib import suppress

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager

config_manager = ConfigManager()

username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def main() -> None:
    """Run the main function."""
    async with ChaturbateClient(username, token, 20, testbed=True) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                logging.info(event.dict())

            # Update the URL for the next request
            url = str(response.next_url)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
