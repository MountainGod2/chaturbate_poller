"""Example demonstrating custom event handlers for large tips."""

import asyncio
import logging
from dataclasses import dataclass

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager, format_message
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User

LARGE_TIP_THRESHOLD = 100
MEGA_TIP_THRESHOLD = 500
BIG_TIP_THRESHOLD = 200

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


@dataclass
class TipHandler:
    """Handler for processing large tips."""

    threshold: int

    async def handle_tip(self, tip: Tip, user: User, event: Event) -> None:
        """Handle incoming tips."""
        formatted_message = format_message(event)
        if formatted_message:
            logger.info(formatted_message)

        if tip.tokens >= self.threshold:
            logger.info("LARGE TIP ALERT! %d tokens from %s!", tip.tokens, user.username)
            await self.send_special_thanks(user.username, tip.tokens)

    async def send_special_thanks(self, username: str, amount: int) -> None:
        """Send special thanks for large tips."""
        if amount >= MEGA_TIP_THRESHOLD:
            logger.info("MEGA TIP! Special VIP thanks to %s for %d tokens!", username, amount)
        elif amount >= BIG_TIP_THRESHOLD:
            logger.info("BIG TIP! Extra special thanks to %s for %d tokens!", username, amount)
        else:
            logger.info("Special thanks to %s for the generous %d token tip!", username, amount)


async def monitor_events(client: ChaturbateClient, handler: TipHandler) -> None:
    """Monitor events."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                if event.method == "tip" and event.object.tip and event.object.user:
                    await handler.handle_tip(event.object.tip, event.object.user, event)
                else:
                    formatted_message = format_message(event)
                    if formatted_message:
                        logger.info(formatted_message)
            url = response.next_url

    except asyncio.CancelledError:
        logger.info("Event monitoring stopped by user")
    except Exception:
        logger.exception("Error occurred while monitoring events")


async def main() -> None:
    """Main function."""
    config_manager = ConfigManager()

    username = config_manager.get("CB_USERNAME", "")
    token = config_manager.get("CB_TOKEN", "")

    if not username or not token:
        logger.error("Please set CB_USERNAME and CB_TOKEN in your environment.")
        logger.info("You can create a .env file or export them as environment variables.")
        return

    logger.info("Starting large tip handler")
    logger.info("Using testbed environment")
    logger.info("Monitoring for tips >= %d tokens", LARGE_TIP_THRESHOLD)

    async with ChaturbateClient(username, token, testbed=True) as client:
        handler = TipHandler(threshold=LARGE_TIP_THRESHOLD)
        try:
            await monitor_events(client, handler)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(main())
