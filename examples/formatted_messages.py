"""Example for the Chaturbate Poller module."""  # noqa: INP001

import asyncio
import logging
import os

import httpx
from chaturbate_poller import ChaturbateClient
from chaturbate_poller.constants import TESTBED_BASE_URL
from chaturbate_poller.format_messages import format_message
from dotenv import load_dotenv

logger = logging.getLogger()


load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


async def main() -> None:
    """Fetch Chaturbate events."""
    async with ChaturbateClient(username, token, base_url=TESTBED_BASE_URL) as client:
        url = None  # Ensure url starts as None or a valid URL string
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

                # Convert next_url to string if not None, otherwise keep as None
                url = str(response.next_url) if response.next_url else None

        # Handle exceptions
        except (KeyboardInterrupt, asyncio.CancelledError, httpx.HTTPError):
            logger.exception("Stopped due to an error.")
        finally:
            # Close the client
            await client.client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
