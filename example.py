# chaturbate_poller/example.py
"""Example for the Chaturbate Poller module."""

import asyncio
import contextlib
import logging
import os

import httpx
from chaturbate_poller import ChaturbateClient
from chaturbate_poller.models import Event
from dotenv import load_dotenv

logger = logging.getLogger()


load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


async def handle_event(event: Event) -> None:  # noqa: C901, PLR0915, PLR0912
    """Handle different types of events."""
    method = event.method
    object_data = event.object

    event_id = event.id

    if method == "broadcastStart":
        logger.info("Broadcast started", extra={"event_id": event_id})
    elif method == "broadcastStop":
        logger.info("Broadcast stopped")
    elif method == "userEnter":
        if object_data.user:
            logger.info("%s entered the room", object_data.user.username)
        else:
            logger.info("User entered the room", extra={"event_id": event_id})
    elif method == "userLeave":
        if object_data.user:
            logger.info("%s left the room", object_data.user.username)
        else:
            logger.info("User left the room")
    elif method == "follow":
        if object_data.user:
            logger.info("%s has followed", object_data.user.username)
        else:
            logger.info("Unknown user has followed")
    elif method == "unfollow":
        if object_data.user:
            logger.info("%s has unfollowed", object_data.user.username)
        else:
            logger.info("Unknown user has unfollowed")
    elif method == "fanclubJoin":
        if object_data.user:
            logger.info("%s joined the fan club", object_data.user.username)
        else:
            logger.info("Unknown user joined the fan club")
    elif method == "chatMessage":
        if object_data.message:
            logger.info(
                "%s sent chat message: %s",
                object_data.message.from_user,
                object_data.message.message,
            )
        else:
            logger.info("Received chat message")
    elif method == "privateMessage":
        if object_data.message:
            logger.info(
                "%s sent private message to %s: %s",
                object_data.message.from_user,
                object_data.message.to_user,
                object_data.message.message,
            )
        else:
            logger.info("Received private message")
    elif method == "tip":
        if object_data.user and object_data.tip:
            anon_message = "anonymously" if object_data.tip.is_anon else ""
            tip_message = (
                f" with message: {object_data.tip.message}"
                if object_data.tip.message
                else ""
            )
            logger.info(
                "%s sent %s tokens %s%s",
                object_data.user.username,
                object_data.tip.tokens,
                anon_message,
                tip_message,
            )
        else:
            logger.info("Received tip")
    elif method == "roomSubjectChange":
        if object_data.subject:
            logger.info("Room Subject changed to %s", object_data.subject)
        else:
            logger.info("Room Subject changed")
    elif method == "mediaPurchase":
        if object_data.user and object_data.media:
            logger.info(
                "%s purchased %s set: %s",
                object_data.user.username,
                object_data.media.type,
                object_data.media.name,
            )
        else:
            logger.info("Received media purchase event")
    else:
        logger.info("Unknown method: %s", method)


async def main() -> None:
    """Fetch Chaturbate events."""
    async with ChaturbateClient(username, token) as client:
        url = None
        try:
            while True:
                response = await client.fetch_events(url=url)
                for event in response.events:
                    await handle_event(event)

                logger.debug("Next URL: %s", response.next_url)
                url = response.next_url if response.next_url else None

        except (KeyboardInterrupt, asyncio.CancelledError, httpx.HTTPError):
            pass
        finally:
            await client.client.aclose()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
