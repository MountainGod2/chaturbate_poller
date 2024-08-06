"""Main module for the Chaturbate Poller."""

import argparse
import asyncio
import logging
import os
from contextlib import suppress

from dotenv import load_dotenv

from chaturbate_poller import ChaturbateClient, __version__

# Load environment variables
load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Run the main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Poll events from Chaturbate.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()

    # Check for missing environment variables
    if not username or not token:
        logging.error("CB_USERNAME and CB_TOKEN environment variables must be set.")
        return

    # Main async logic
    async with ChaturbateClient(
        username, token, 20, "https://events.testbed.cb.dev/events/{username}/{token}/"
    ) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                logging.info(event.dict())
            url = str(response.next_url)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
