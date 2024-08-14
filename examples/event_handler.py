"""Example of fetching Chaturbate events and printing only large tips."""

import asyncio
import logging
import os
from contextlib import suppress

from dotenv import load_dotenv

from chaturbate_poller.client import ChaturbateClient
from chaturbate_poller.models import Tip, User

LARGE_TIP_THRESHOLD = 100

load_dotenv()
logging.basicConfig(level=logging.INFO)

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


async def tip_handler(tip: Tip, user: User) -> None:
    """Print a message for large tips.

    Args:
        tip (Tip): The tip object.
        user (User): The user object.
    """
    if tip.tokens >= LARGE_TIP_THRESHOLD:
        logging.info("User %s tipped %d tokens!", user.username, tip.tokens)


async def main() -> None:
    """Example of fetching Chaturbate events and printing only large tips."""
    async with ChaturbateClient(username, token, testbed=True) as client:
        url: str | None = None

        while True:
            response = await client.fetch_events(url=url)
            for event in response.events:
                if event.method == "tip":
                    tip = event.object.tip
                    user = event.object.user
                    if tip and user:
                        await tip_handler(tip, user)

            if response.next_url is None:
                break

            url = str(response.next_url)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
