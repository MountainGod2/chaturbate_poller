# /// script
# dependencies = [
#   "chaturbate-poller==1.17.1",
#   "pystray==0.19.5",
#   "pillow==11.1.0"
# ]
# requires-python = ">=3.12"
# ///

"""Chaturbate Poller System Tray Application.

Runs in the background and displays notifications for events.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any
import threading

# Third-party imports for the GUI
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# Import Chaturbate Poller components
from chaturbate_poller import ChaturbateClient, ConfigManager, format_message, __version__
from chaturbate_poller.constants import API_TIMEOUT

# Set up logging to file instead of console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("chaturbate_poller.log")]
)
logger = logging.getLogger(__name__)

# Global variables
running = True
client: ChaturbateClient|None = None
event_queue= asyncio.Queue()
config = ConfigManager()

def create_icon():
    """Create a simple icon for the system tray."""
    width = 64
    height = 64
    color1 = (255, 128, 0)
    color2 = (0, 0, 0)

    image = Image.new('RGB', (width, height), color2)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, 3 * width // 4, 3 * height // 4),
        fill=color1
    )
    return image

def notify(title: str, message: str):
    """Display a notification."""
    if icon and icon.visible:
        icon.notify(message, title)
        logger.info(f"Notification: {title} - {message}")

async def process_events():
    """Process events from the Chaturbate API."""
    global client

    username: str | None = config.get(key="CB_USERNAME", default="")
    token: str | None = config.get(key="CB_TOKEN", default="")

    if not username or not token:
        notify(title="Configuration Error", message="Please set CB_USERNAME and CB_TOKEN in your configuration.")
        logger.error("Missing credentials in configuration")
        return

    async with ChaturbateClient(
        username=username,
        token=token,
        timeout=API_TIMEOUT,
        testbed=False
    ) as client:

        url: str|None = None

        try:
            while running:
                try:
                    response = await client.fetch_events(url)
                    for event in response.events:
                        formatted_message = format_message(event)
                        message = formatted_message if formatted_message else "No message"
                        notify(title=f"Chaturbate Event ({event.method})", message=message)
                        await event_queue.put(item={
                            'timestamp': datetime.now().isoformat(),
                            'type': event.method,
                            'message': message
                        })
                    url: str | None = response.next_url
                    await asyncio.sleep(5)
                except Exception:
                    logger.exception("Error fetching events.")
                    await asyncio.sleep(30)  # Longer wait on error
        except asyncio.CancelledError:
            logger.info("Event processing cancelled")


def exit_action(icon: pystray.Icon):
    """Stop the application when exit is selected."""
    global running
    running = False
    icon.stop()

def show_about() -> None:
    """Show about information."""
    notify(title="About Chaturbate Poller",
           message=f"Chaturbate Poller running in the background.\nVersion: {__version__}")

def create_menu():
    """Create the system tray menu."""
    return (
        item('About', show_about),
        item('Exit', exit_action),
    )

async def main_async() -> None:
    """Asynchronous main function."""
    event_processor = asyncio.create_task(process_events())

    # Keep the async part running
    while running:
        await asyncio.sleep(1)

    # Clean up
    event_processor.cancel()
    try:
        await event_processor
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    # Create and run the system tray icon
    icon = pystray.Icon("chaturbate-poller", create_icon(), "Chaturbate Poller", create_menu())

    # Run the icon in a separate thread
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

    # We need to run the asyncio loop in the main thread
    asyncio.run(main_async())
    sys.exit(0)
