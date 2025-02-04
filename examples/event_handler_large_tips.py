import asyncio
import logging
from dataclasses import dataclass

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager
from chaturbate_poller.models import Tip, User

LARGE_TIP_THRESHOLD = 100  # Set the threshold for large tips

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


@dataclass
class TipHandler:
    """Handler for processing large tips."""

    threshold: int

    async def handle_tip(self, tip: Tip, user: User) -> None:
        """Handle incoming tips that meet the threshold."""
        if tip.tokens >= self.threshold:
            logger.info("Large tip received! %d tokens from %s", tip.tokens, user.username)
            # Add your custom handling logic here


async def monitor_events(client: ChaturbateClient, handler: TipHandler) -> None:
    """Monitor events and process tips."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                if event.method == "tip" and event.object.tip and event.object.user:
                    await handler.handle_tip(event.object.tip, event.object.user)
            url = response.next_url

    except asyncio.CancelledError:
        logger.info("Event monitoring stopped")
    except Exception:
        logger.exception("Error monitoring events")


async def main() -> None:
    config_manager = ConfigManager()

    username = config_manager.get("CB_USERNAME", "")
    token = config_manager.get("CB_TOKEN", "")

    async with ChaturbateClient(username, token, testbed=True) as client:
        handler = TipHandler(threshold=LARGE_TIP_THRESHOLD)
        await monitor_events(client, handler)


if __name__ == "__main__":
    asyncio.run(main())
