"""Example for the Chaturbate Poller module."""

import asyncio
import logging
from contextlib import suppress

import httpx

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager
from chaturbate_poller.format_messages import format_message

logger = logging.getLogger()


config_manager = ConfigManager()

username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def main() -> None:
    """Fetch Chaturbate events."""
    async with ChaturbateClient(username, token, testbed=True) as client:
        url = None  # Ensure url starts as None or a valid URL string
        logger.info("Fetching Chaturbate events.")
        try:
            while True:
                # Make sure url is a string when passed to fetch_events
                response = await client.fetch_events(url=url)

                # Handle each event in the response
                for event in response.events:
                    message = await format_message(event)

                    # Log the formatted message
                    logger.info(message)

                # Log the next URL for debugging purposes
                logger.debug("Next URL: %s", response.next_url)

                # Update the URL for the next request
                url = str(response.next_url)

        # Handle exceptions
        except (httpx.HTTPStatusError, httpx.ReadError, ValueError) as exc:
            logger.error("An error occurred: %s", exc)  # noqa: TRY400

        # Ensure the client is closed
        finally:
            await client.client.aclose()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt, asyncio.CancelledError):
        asyncio.run(main())
