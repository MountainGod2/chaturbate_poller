import asyncio
import logging

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager

# Configure rich logging
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


async def poll_events(client: ChaturbateClient) -> None:
    """Poll and log events with proper error handling."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                logger.info("Event received: %s", event.model_dump(exclude_none=True))
            url = response.next_url
    except asyncio.CancelledError:
        logger.info("Polling cancelled")
    except Exception:
        logger.exception("Error polling events")


async def main() -> None:
    """Main application entry point with config validation."""
    config = ConfigManager()

    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    if not username or not token:
        logger.error("Please set CB_USERNAME and CB_TOKEN in your environment.")
        return

    async with ChaturbateClient(username, token, testbed=True) as client:
        try:
            await poll_events(client)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
