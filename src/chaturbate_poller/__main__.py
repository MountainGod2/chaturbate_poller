"""Main module for the Chaturbate Poller."""

import asyncio
import contextlib
import logging
import os

import httpx
from dotenv import load_dotenv

from . import ChaturbateClient

logger = logging.getLogger(__package__)


load_dotenv()

username = os.getenv("CB_USERNAME", "")
"""str: The Chaturbate username."""
token = os.getenv("CB_TOKEN", "")
"""str: The Chaturbate token."""


async def main() -> None:
    """Fetch Chaturbate events.

    Raises:
        KeyboardInterrupt: If the user interrupts the program.
        httpx.HTTPError: If an error occurs fetching events.

    """
    async with ChaturbateClient(username, token) as client:
        url = None
        try:
            logger.info("Starting cb_poller module. Press Ctrl+C to stop.")
            while True:
                response = await client.fetch_events(url=url)
                for event in response.events:
                    logger.info("Event: %s", event)

                logger.debug("Next URL: %s", response.next_url)
                url = response.next_url if response.next_url else None

        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.debug("Cancelled fetching Chaturbate events.")
        except httpx.HTTPError:
            logger.warning("Error fetching Chaturbate events.")
        finally:
            logger.info("Stopping cb_poller module.")


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
