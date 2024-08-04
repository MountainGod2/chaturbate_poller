# ruff: noqa: INP001,D100,D103,ARG001,S106,T201
import asyncio
import contextlib
import logging
import os

from dotenv import load_dotenv

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller
from chaturbate_event_listener.logging_config import setup_logging
from chaturbate_event_listener.models import Event, Message, Tip, User

load_dotenv()
setup_logging(debug=False)
logger = logging.getLogger("example.py")


def handle_tip_event(event: Event) -> None:
    user: User | None = event.object.user
    tip: Tip | None = event.object.tip

    if user and tip and user.username and tip.tokens:
        logger.info("%s tipped %s tokens", user.username, tip.tokens)


def handle_chat_message_event(event: Event) -> None:
    user: User | None = event.object.user
    message: Message | None = event.object.message

    if user and message and user.username and message.message:
        logger.info("%s sent chat message: %s", user.username, message.message)


async def main() -> None:
    config = Config(
        username=os.getenv("CHATURBATE_USERNAME", ""),
        token=os.getenv("CHATURBATE_TOKEN", ""),
        use_testbed=True,
        influxdb_url=os.getenv("INFLUXDB_URL"),
        influxdb_token=os.getenv("INFLUXDB_TOKEN"),
        influxdb_org=os.getenv("INFLUXDB_ORG"),
        influxdb_bucket=os.getenv("INFLUXDB_BUCKET"),
        event_store_type=os.getenv("EVENT_STORE_TYPE", "console"),
    )
    poller = EventPoller(config)

    poller.register_callback("tip", handle_tip_event)
    poller.register_callback("chatMessage", handle_chat_message_event)

    await poller.poll()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, asyncio.CancelledError, SystemExit):
        asyncio.run(main())
