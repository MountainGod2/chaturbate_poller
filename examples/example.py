# ruff: noqa: INP001,D100,D103,ARG001,S106,T201
import asyncio
import contextlib
import os

from dotenv import load_dotenv

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller
from chaturbate_event_listener.models import Event

load_dotenv()


def handle_tip_event(event: Event) -> None:
    if (
        event.object.user
        and event.object.tip
        and event.object.user.username
        and event.object.tip.tokens
    ):
        print(f"{event.object.user.username} tipped: " f"{event.object.tip.tokens} tokens")


def handle_chat_message_event(event: Event) -> None:
    if (
        event.object.user
        and event.object.message
        and event.object.user.username
        and event.object.message.message
    ):
        print(f"{event.object.user.username}: {event.object.message.message}")


async def main() -> None:
    config = Config(
        username=os.environ.get("CHATURBATE_USERNAME", ""),
        token=os.environ.get("CHATURBATE_TOKEN", ""),
        use_testbed=True,
    )
    poller = EventPoller(config)

    poller.register_callback("tip", handle_tip_event)
    poller.register_callback("chatMessage", handle_chat_message_event)

    await poller.poll()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, asyncio.CancelledError, SystemExit):
        asyncio.run(main())
