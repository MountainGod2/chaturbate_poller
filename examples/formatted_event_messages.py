"""Example demonstrating event message formatting."""

import asyncio
import logging

from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager, format_message

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


async def process_events(client: ChaturbateClient) -> None:
    """Process and format events."""
    url: str | None = None

    try:
        while True:
            response = await client.fetch_events(url)
            for event in response.events:
                formatted_message = format_message(event)
                if formatted_message:
                    logger.info(formatted_message)
                else:
                    logger.debug("Unhandled event type: %s", event.method)
            url = response.next_url
    except asyncio.CancelledError:
        logger.info("Event processing cancelled by user")
    except Exception:
        logger.exception("Error occurred while processing events")


async def main() -> None:
    """Main application entry point."""
    config = ConfigManager()

    username = config.get("CB_USERNAME", default="")
    token = config.get("CB_TOKEN", default="")

    if not username or not token:
        logger.error("Please set CB_USERNAME and CB_TOKEN in your environment.")
        logger.info("You can create a .env file or export them as environment variables.")
        return

    logger.info("Starting event message formatting demo")
    logger.info("Using testbed environment")

    async with ChaturbateClient(username, token, testbed=True) as client:
        try:
            await process_events(client)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    asyncio.run(main())
