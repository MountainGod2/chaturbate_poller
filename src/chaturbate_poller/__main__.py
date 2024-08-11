"""Main module for the Chaturbate Poller."""

import argparse
import asyncio
import logging
import os
from contextlib import suppress
from logging.config import dictConfig

from dotenv import load_dotenv

from chaturbate_poller import ChaturbateClient, __version__
from chaturbate_poller.logging_config import LOGGING_CONFIG

# Configure logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def parse_arguments() -> argparse.Namespace:  # pragma: no cover
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Poll events from Chaturbate.")
    parser.add_argument("--version", action="version", version=f"chaturbate_poller {__version__}")
    parser.add_argument("--testbed", action="store_true", help="Use the testbed environment")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for the API requests")
    parser.add_argument(
        "--username",
        type=str,
        default=os.getenv("CB_USERNAME", ""),
        help="Chaturbate username (default: from environment variable)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.getenv("CB_TOKEN", ""),
        help="Chaturbate token (default: from environment variable)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


async def start_polling(
    username: str, token: str, timeout: int, *, testbed: bool, verbose: bool
) -> None:
    """Start polling Chaturbate events."""
    if verbose is True:
        logging.getLogger("chaturbate_poller").setLevel(logging.DEBUG)
    if not username or not token:
        logging.error(
            "CB_USERNAME and CB_TOKEN must be provided as arguments or environment variables."
        )
        return

    async with ChaturbateClient(username, token, timeout=timeout, testbed=testbed) as client:
        url = None
        while True:
            response = await client.fetch_events(url)
            if response is None:
                break
            url = str(response.next_url)


def main() -> None:  # pragma: no cover
    """Run the main function within an asyncio event loop."""
    args = parse_arguments()
    with suppress(KeyboardInterrupt):
        asyncio.run(
            start_polling(
                args.username, args.token, args.timeout, testbed=args.testbed, verbose=args.verbose
            )
        )


if __name__ == "__main__":  # pragma: no cover
    main()
