import asyncio
import logging

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


async def poll_events(client: ChaturbateClient) -> None:
    """Poll for events continuously and handle them."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                logger.info("Received event: %s", event.model_dump())
            url = response.next_url

    except asyncio.CancelledError:
        logger.info("Polling stopped")
    except Exception:
        logger.exception("Error while polling events")


async def main() -> None:
    """Main application entry point."""
    config = ConfigManager()

    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    async with ChaturbateClient(username, token) as client:
        try:
            await poll_events(client)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
