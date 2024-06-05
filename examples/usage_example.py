"""Example usage of the Chaturbate Events API client."""  #  # noqa: INP001

import asyncio
from typing import Any

from chaturbate_event_listener.client import ChaturbateEventClient
from chaturbate_event_listener.config import CHATURBATE_TOKEN, CHATURBATE_USERNAME
from chaturbate_event_listener.logger import logger


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
    """Main function to run the event listener."""
    user = CHATURBATE_USERNAME
    apitoken = CHATURBATE_TOKEN

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
