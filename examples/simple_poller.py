import asyncio  # noqa: INP001, D100
import logging
import os

from chaturbate_poller import ChaturbateClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("CB_USERNAME", "")
token = os.getenv("CB_TOKEN", "")


async def main() -> None:  # noqa: D103
    async with ChaturbateClient(
        username, token, 20, "https://events.testbed.cb.dev/events/{username}/{token}/"
    ) as client:
        response = await client.fetch_events()
        for event in response.events:
            logging.info(event.dict())


if __name__ == "__main__":
    asyncio.run(main())
