import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final

from phue import Bridge, PhueException
from rich.logging import RichHandler
from tenacity import retry, stop_after_attempt, wait_exponential

from chaturbate_poller import ChaturbateClient, ConfigManager
from chaturbate_poller.models import Event, Tip

# Constants
DEFAULT_HUE_IP: Final = "192.168.0.23"
FLASH_DELAY: Final = 0.5
MAX_RETRIES: Final = 3
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
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("hue_controller")


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
        self._lights: list[str] = []
        self._update_lights()
        self._color_timer: asyncio.Task | None = None

    def _update_lights(self) -> None:
        """Update the list of available lights."""
        if self.bridge.lights:
            self._lights = [light.light_id for light in self.bridge.lights]
        else:
            self._lights = []

    async def _revert_lights(self, delay: float) -> None:
        """Revert lights to default state after delay."""
        await asyncio.sleep(delay)
        try:
            self.bridge.set_light(self._lights, {"on": True, "bri": 254, "xy": [0.3227, 0.329]})
        except PhueException:
            logger.warning("Error reverting lights to default state")

    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
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

            # Set new color
            xy = COLOR_COMMANDS[color.lower()]
            self.bridge.set_light(self._lights, {"on": True, "bri": 254, "xy": xy})
            logger.info("Setting lights to %s", color)

            # Start new timer
            self._color_timer = asyncio.create_task(self._revert_lights(COLOR_TIMEOUT))

        except PhueException:
            logger.warning("Error setting lights to %s", color)


class EventHandler:
    """Event handler for processing Chaturbate events."""

    def __init__(self, hue_controller: HueController, config: ConfigManager) -> None:
        """Initialize the event handler."""
        self.hue = hue_controller
        self.config = config
        self.tip_threshold = int(config.get("LARGE_TIP_THRESHOLD", "100"))

    async def handle_event(self, event: Event) -> None:
        """Handle incoming events."""
        if isinstance(event.object.tip, Tip):
            await self.handle_tip(event.object.tip)

    async def handle_tip(self, tip: Tip) -> None:
        """Handle incoming tip events."""
        logger.info("Received tip of %d tokens", tip.tokens)
        if tip.tokens >= REQUIRED_TOKENS and tip.message:
            # Check if any color word is in the message
            message_words = tip.message.lower().split()
            for color in COLOR_COMMANDS:
                if color in message_words:
                    await self.hue.set_color(color)
                    break


class EventMonitor:
    """Monitor Chaturbate events and control Hue lights."""

    def __init__(self, event_handler: EventHandler, client: ChaturbateClient) -> None:
        """Initialize the Event Monitor."""
        self.event_handler = event_handler
        self.client = client
        self.running = True

    async def monitor_events(self) -> None:
        """Monitor Chaturbate events with improved error handling."""
        url: str | None = None

        while self.running:
            try:
                response = await self.client.fetch_events(url)
                for event in response.events:
                    await self.event_handler.handle_event(event)
                url = response.next_url

            except asyncio.CancelledError:
                self.running = False
                break
            except Exception:
                logger.exception("Error monitoring events")
                await asyncio.sleep(5)

    def stop(self) -> None:
        """Gracefully stop the monitor."""
        self.running = False


async def setup_hue_bridge(
    ip_address: str,
) -> Bridge:
    """Setup and connect to the Hue Bridge."""
    logger.info("Connecting to Hue Bridge at %s", ip_address)
    try:
        bridge = Bridge(ip_address)
        bridge.connect()
    except PhueException as exc:
        logger.warning("Error connecting to Hue Bridge")
        raise exc from None
    return bridge


async def main() -> None:
    """Main application entry point."""
    config = ConfigManager()

    # Validate configuration
    required_configs = {
        "CB_USERNAME": config.get("CB_USERNAME"),
        "CB_TOKEN": config.get("CB_TOKEN"),
        "HUE_BRIDGE_IP": config.get("HUE_BRIDGE_IP", DEFAULT_HUE_IP),
    }

    if not all(required_configs.values()):
        msg = (
            f"Missing required configurations: {[k for k, v in required_configs.items() if not v]}"
        )
        raise ValueError(msg)

    username = required_configs["CB_USERNAME"]
    token = required_configs["CB_TOKEN"]
    hue_ip = required_configs["HUE_BRIDGE_IP"]

    bridge = await setup_hue_bridge(hue_ip)
    hue_controller = HueController(bridge)
    event_handler = EventHandler(hue_controller, config)

    async with ChaturbateClient(username, token, testbed=True) as client:
        monitor = EventMonitor(event_handler, client)
        try:
            await monitor.monitor_events()
        except asyncio.CancelledError:
            monitor.stop()
            logger.info("Shutting down gracefully...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except PhueException as exc:
        logger.warning("Error communicating with Hue Bridge: %s", exc)
    except Exception:
        logger.exception("Fatal error occurred")
