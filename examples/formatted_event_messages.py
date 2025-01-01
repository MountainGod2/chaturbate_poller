import asyncio
import logging

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager, format_message

# Configure rich logging
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


async def process_events(client: ChaturbateClient) -> None:
    """Process and format events with error handling."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                message = await format_message(event)
                logger.info(message)
            url = response.next_url
    except asyncio.CancelledError:
        logger.info("Event processing cancelled")
    except Exception:
        logger.exception("Error processing events")


async def main() -> None:
    """Main application entry point with config validation."""
    config = ConfigManager()

    username = config.get("CB_USERNAME", "")
    token = config.get("CB_TOKEN", "")

    async with ChaturbateClient(username, token, testbed=True) as client:
        try:
            await process_events(client)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())
