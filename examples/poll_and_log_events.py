import asyncio
import logging
from contextlib import suppress

from chaturbate_poller.chaturbate_client import ChaturbateClient
from chaturbate_poller.config_manager import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_manager = ConfigManager()
username = config_manager.get("CB_USERNAME", "")
token = config_manager.get("CB_TOKEN", "")


async def main():
    async with ChaturbateClient(username, token) as client:
        url = None

        while True:
            response = await client.fetch_events(url)

            for event in response.events:
                logger.info(event.dict())

            url = response.next_url


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
