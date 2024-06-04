"""Example usage of the Chaturbate Events API client."""  #  # noqa: INP001

import asyncio
import os
from typing import Any

from dotenv import load_dotenv

from chaturbate_event_listener.client import ChaturbateEventClient
from chaturbate_event_listener.logger import logger

load_dotenv()


def handle_event(message: dict[str, Any]) -> None:
    """Custom event handler.

    Simply logs the message ID and method. This function can be replaced with a custom
    event handler function that processes the event messages as needed.

    Args:
        message (dict[str, Any]): The event message.
    """
    logger.info(f"Message ID: {message.get('id')}")
    logger.info(f"Method: {message.get('method')}")


async def main() -> None:
    """Run the Chaturbate Events API client."""
    user = os.getenv("CHATURBATE_USERNAME", "")
    apitoken = os.getenv("CHATURBATE_TOKEN", "")

    client = ChaturbateEventClient(
        username=user,
        token=apitoken,
        event_handler=handle_event,
        is_testbed=True,
    )

    async with client:
        await client.process_events()


if __name__ == "__main__":
    asyncio.run(main())
