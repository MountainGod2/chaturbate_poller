"""Example of using the Chaturbate Poller to fetch events."""

import asyncio
import logging
import os
from contextlib import suppress

from dotenv import load_dotenv

from chaturbate_poller import ChaturbateClient

load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


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
