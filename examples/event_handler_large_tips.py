import asyncio
import logging
from contextlib import suppress

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager

LARGE_TIP_THRESHOLD = 100  # Set the threshold for large tips

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_manager = ConfigManager()
username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def handle_large_tip(tip, user):
    if tip.tokens >= LARGE_TIP_THRESHOLD:
        logger.info("User %s tipped %s tokens!", user.username, tip.tokens)


async def main():
    async with ChaturbateClient(username, token) as client:
        url = None

        while True:
            response = await client.fetch_events(url)

            for event in response.events:
                if event.method == "tip":
                    tip = event.object.tip
                    user = event.object.user
                    if tip and user:
                        await handle_large_tip(tip, user)

            url = response.next_url


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
