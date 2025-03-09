# /// script
# dependencies = [
#   "chaturbate-poller==1.12.1",
#   "phue==1.1",
# ]
# requires-python = ">=3.12"
# ///

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from logging import Logger
from typing import TYPE_CHECKING, Final

from phue import Bridge, PhueException
from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.tip import Tip

if TYPE_CHECKING:
    from chaturbate_poller.models.api_response import EventsAPIResponse

# Constants
DEFAULT_HUE_IP: Final = "192.168.0.23"
FLASH_DELAY: Final = 0.5
REQUIRED_TOKENS: Final = 35
COLOR_TIMEOUT: Final = 600  # 10 minutes in seconds
COLOR_COMMANDS: Final = {
    "red": [0.6750, 0.3220],
    "orange": [0.6000, 0.3600],
    "yellow": [0.5, 0.4],
    "green": [0.2151, 0.7106],
    "blue": [0.1538, 0.0600],
    "indigo": [0.2000, 0.1000],
    "violet": [0.2651, 0.1241],
}

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
)
# Suppress httpx debug logs
logging.getLogger(name="httpx").setLevel(level=logging.WARNING)
logger: Logger = logging.getLogger(name="hue_controller")


class LightEffect(Enum):
    """Enumeration of light effects."""

    FLASH = auto()
    PULSE = auto()
    RAINBOW = auto()


@dataclass
class LightConfig:
    """Configuration for light effects."""

    brightness: int = 254
    transition_time: int = 1
    effect: LightEffect = LightEffect.FLASH
    num_flashes: int = 3
    lights: list[str] = field(default_factory=list)


class HueController:
    """Controller for managing Hue lights on the bridge."""

    def __init__(self, bridge: Bridge) -> None:
        """Initialize the Hue Controller."""
        self.bridge: Bridge = bridge
        self._lights: list[int] = []
        self._update_lights()
        self._color_timer: asyncio.Task[None] | None = None

    def _update_lights(self) -> None:
        """Update the list of available lights."""
        light_objects = self.bridge.get_light_objects()
        if isinstance(light_objects, list):
            self._lights = [light.light_id for light in light_objects]
        else:
            self._lights = []

    async def _revert_lights(self, delay: float) -> None:
        """Revert lights to default state after delay."""
        await asyncio.sleep(delay)
        try:
            for light_id in self._lights:
                self.bridge.set_light(light_id, {"on": True, "bri": 254, "xy": [0.3227, 0.329]})
        except PhueException:
            logger.warning("Error reverting lights to default state")

    async def set_color(self, color: str) -> None:
        """Set lights to specified color and schedule reversion."""
        if not self._lights:
            logger.warning("No lights found on the Hue Bridge!")
            return

        if color.lower() not in COLOR_COMMANDS:
            logger.warning("Invalid color specified: %s", color)
            return

        try:
            # Cancel existing timer if there is one
            if self._color_timer and not self._color_timer.done():
                self._color_timer.cancel()

            # Set lights to specified color
            xy: list[float] = COLOR_COMMANDS[color.lower()]
            for light_id in self._lights:
                self.bridge.set_light(light_id, {"on": True, "bri": 254, "xy": xy})
            logger.info("Setting lights to %s", color)

            # Start new timer
            self._color_timer = asyncio.create_task(self._revert_lights(delay=COLOR_TIMEOUT))

        except PhueException:
            logger.warning("Error setting lights to %s", color)


class EventHandler:
    """Event handler for processing Chaturbate events."""

    def __init__(self, hue_controller: HueController, config: ConfigManager) -> None:
        """Initialize the event handler."""
        self.hue: HueController = hue_controller
        self.config: ConfigManager = config
        tip_threashold: str | None = self.config.get(key="TIP_THRESHOLD")
        if tip_threashold:
            self.tip_threshold: int = int(tip_threashold)
        else:
            self.tip_threshold = REQUIRED_TOKENS

    async def handle_event(self, event: Event) -> None:
        """Handle incoming events."""
        if isinstance(event.object.tip, Tip):
            await self.handle_tip(tip=event.object.tip)

    async def handle_tip(self, tip: Tip) -> None:
        """Handle incoming tip events."""
        logger.info("Received tip of %d tokens", tip.tokens)
        if tip.tokens >= REQUIRED_TOKENS and tip.message:
            # Check if any color word is in the message
            message_words: list[str] = tip.message.lower().split()
            for color in COLOR_COMMANDS:
                if color in message_words:
                    await self.hue.set_color(color)
                    break


class EventMonitor:
    """Monitor Chaturbate events and control Hue lights."""

    def __init__(self, event_handler: EventHandler, client: ChaturbateClient) -> None:
        """Initialize the Event Monitor."""
        self.event_handler: EventHandler = event_handler
        self.client: ChaturbateClient = client
        self.running: bool = True

    async def monitor_events(self) -> None:
        """Monitor Chaturbate events with improved error handling."""
        url: str | None = None

        while self.running:
            try:
                response: EventsAPIResponse = await self.client.fetch_events(url)
                for event in response.events:
                    await self.event_handler.handle_event(event)
                url: str | None = response.next_url

            except asyncio.CancelledError:
                self.running = False
                break
            except Exception:
                logger.exception("Error monitoring events")
                await asyncio.sleep(5)

    def stop(self) -> None:
        """Gracefully stop the monitor."""
        self.running = False


def setup_hue_bridge(
    ip_address: str,
) -> Bridge:
    """Setup and connect to the Hue Bridge.

    Args:
        ip_address (str): The IP address of the Hue Bridge.

    Returns:
        Bridge: The connected Hue Bridge.

    Raises:
        PhueException: If an error occurs while connecting to the bridge.
    """
    logger.info("Connecting to Hue Bridge at %s", ip_address)
    try:
        bridge: Bridge = Bridge(ip_address)
        bridge.connect()
    except PhueException:
        logger.exception("Error connecting to Hue Bridge")
        raise
    return bridge


async def main() -> None:
    """Main application entry point.

    Raises:
        ValueError: If required configurations are missing.
    """
    config: ConfigManager = ConfigManager()

    username: str | None = config.get(key="CHATURBATE_USERNAME")
    if not username:
        msg = "CHATURBATE_USERNAME is required in the configuration"
        raise ValueError(msg)
    token: str | None = config.get(key="CHATURBATE_TOKEN")
    if not token:
        msg = "CHATURBATE_TOKEN is required in the configuration"
        raise ValueError(msg)
    bridge_ip: str | None = config.get(key="HUE_IP", default=None)
    hue_ip: str = bridge_ip or DEFAULT_HUE_IP
    bridge: Bridge = setup_hue_bridge(hue_ip)
    hue_controller: HueController = HueController(bridge)
    event_handler: EventHandler = EventHandler(hue_controller, config)

    async with ChaturbateClient(username, token, testbed=True) as client:
        monitor: EventMonitor = EventMonitor(event_handler, client)
        try:
            await monitor.monitor_events()
        except asyncio.CancelledError:
            monitor.stop()
            logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    try:
        asyncio.run(main=main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except PhueException:
        logger.exception("Error communicating with Hue Bridge")
    except Exception:
        logger.exception("An unexpected error occurred")
    finally:
        logger.info("Exiting...")
