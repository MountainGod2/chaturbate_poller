# /// script
# dependencies = [
#   "chaturbate-poller==3.7.4",
#   "pystray==0.19.5",
#   "pillow==11.2.1",
#   "anyio==4.9.0"
# ]
# requires-python = ">=3.12"
# ///

"""Chaturbate Poller System Tray Application.

Runs in the background and displays notifications for events.
"""

import asyncio
import contextlib
import logging
import sys
import threading
from datetime import UTC, datetime

# Add anyio import
import anyio

# Third-party imports for the GUI
import pystray
from PIL import Image, ImageDraw
from PIL.Image import Image as PILImage
from pystray._base import Icon, MenuItem

# Import Chaturbate Poller components
from chaturbate_poller import ChaturbateClient, ConfigManager, __version__, format_message
from chaturbate_poller.constants import API_TIMEOUT

# Set up logging to file instead of console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("chaturbate_poller.log")],
)
logger = logging.getLogger(__name__)


class ChaturbatePollerApp:
    """Application class for the Chaturbate Poller."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.running = True
        self.client = None
        self.event_queue = asyncio.Queue()
        self.config = ConfigManager()
        self.icon = None
        self.stop_event = anyio.Event()  # Add event for signaling application stop

    def create_icon(self) -> PILImage:
        """Create a simple icon for the system tray."""
        width = 64
        height = 64
        color1 = (12, 106, 147)
        color2 = (244, 115, 33)

        image = Image.new("RGB", (width, height), color2)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 4, height // 4, 3 * width // 4, 3 * height // 4), fill=color1)
        return image

    def notify(self, title: str, message: str) -> None:
        """Display a notification."""
        if self.icon and self.icon.visible:
            self.icon.notify(message, title)
            logger.info("Notification: %s - %s", title, message)

    async def process_events(self) -> None:
        """Process events from the Chaturbate API."""
        username: str | None = self.config.get(key="CB_USERNAME", default="")
        token: str | None = self.config.get(key="CB_TOKEN", default="")

        if not username or not token:
            self.notify(
                title="Configuration Error",
                message="Please set CB_USERNAME and CB_TOKEN in your configuration.",
            )
            logger.error("Missing credentials in configuration")
            sys.exit(1)

        async with ChaturbateClient(
            username=username,
            token=token,
            timeout=API_TIMEOUT,
        ) as self.client:
            url = None

            try:
                while self.running:
                    try:
                        response = await self.client.fetch_events(url)
                        for event in response.events:
                            formatted_message = format_message(event)
                            message = formatted_message if formatted_message else "No message"
                            self.notify(title=f"Chaturbate Event ({event.method})", message=message)
                            await self.event_queue.put(
                                item={
                                    "timestamp": datetime.now(tz=UTC).isoformat(),
                                    "type": event.method,
                                    "message": message,
                                }
                            )
                        url: str | None = response.next_url

                        with contextlib.suppress(TimeoutError):
                            with anyio.move_on_after(5):
                                await self.stop_event.wait()
                        if self.stop_event.is_set():
                            break
                    except Exception:
                        logger.exception("Error fetching events.")
                        with contextlib.suppress(TimeoutError):
                            with anyio.move_on_after(30):
                                await self.stop_event.wait()
                        if self.stop_event.is_set():
                            break
            except asyncio.CancelledError:
                logger.info("Event processing cancelled")

    def exit_action(self, icon: Icon) -> None:
        """Stop the application when exit is selected."""
        self.running = False

        async def set_stop_event() -> None:
            self.stop_event.set()

        asyncio.run_coroutine_threadsafe(set_stop_event(), asyncio.get_event_loop())
        icon.stop()

    def show_about(self) -> None:
        """Show about information."""
        self.notify(
            title="About Chaturbate Poller",
            message=f"Chaturbate Poller running in the background.\nVersion: {__version__}",
        )

    def create_menu(self) -> tuple[MenuItem, MenuItem]:
        """Create the system tray menu."""
        return (
            MenuItem("About", self.show_about),
            MenuItem("Exit", self.exit_action),
        )

    async def main_async(self) -> None:
        """Asynchronous main function."""
        event_processor = asyncio.create_task(self.process_events())

        # Wait for stop event
        await self.stop_event.wait()

        # Clean up
        event_processor.cancel()

    def run(self) -> None:
        """Run the application."""
        self.icon = pystray.Icon(
            "chaturbate-poller", self.create_icon(), "Chaturbate Poller", self.create_menu()
        )

        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.daemon = True
        icon_thread.start()

        asyncio.run(self.main_async())


if __name__ == "__main__":
    app = ChaturbatePollerApp()
    app.run()
    sys.exit(0)
