# /// script
# dependencies = [
#   "chaturbate-poller==1.12.1",
#   "phue==1.1",
# ]
# requires-python = ">=3.12"
# ///

import asyncio
import contextlib
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from logging import Logger
from typing import TYPE_CHECKING, Any, ClassVar

from phue import Bridge, PhueException
from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.tip import Tip

if TYPE_CHECKING:
    from collections.abc import Callable

    from chaturbate_poller.models.api_response import EventsAPIResponse


# Constants
@dataclass(frozen=True)
class HueConfig:
    """Configuration for Hue light commands."""

    DEFAULT_HUE_IP: ClassVar[str] = "192.168.0.23"
    FLASH_DELAY: ClassVar[float] = 0.5
    DEFAULT_REQUIRED_TOKENS: ClassVar[int] = 35
    COLOR_TIMEOUT: ClassVar[int] = 600  # 10 minutes in seconds
    DEFAULT_BRIGHTNESS: ClassVar[int] = 254
    # XY color values for different colors
    COLOR_COMMANDS: ClassVar[dict[str, list[float]]] = {
        "red": [0.6750, 0.3220],
        "orange": [0.6000, 0.3600],
        "yellow": [0.5, 0.4],
        "green": [0.2151, 0.7106],
        "blue": [0.1538, 0.0600],
        "indigo": [0.2000, 0.1000],
        "violet": [0.2651, 0.1241],
        "white": [0.3227, 0.3290],  # Approximate white color
    }
    # Default light state
    DEFAULT_LIGHT_STATE: ClassVar[dict[str, Any]] = {
        "on": True,
        "bri": DEFAULT_BRIGHTNESS,
        "xy": COLOR_COMMANDS["white"],
        "transitiontime": 1,
    }
    # Connection retry settings
    CONNECTION_RETRIES: ClassVar[int] = 3
    RETRY_DELAY: ClassVar[int] = 5  # seconds


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
)
# Suppress httpx debug logs
logging.getLogger(name="httpx").setLevel(level=logging.WARNING)

# Suppress phue debug logs
logging.getLogger(name="phue").setLevel(level=logging.WARNING)


# Create a logger for the script
# This logger will be used for all logging in this script
logger: Logger = logging.getLogger(name="hue_light_control")
logger.info("Starting Hue Light Control script")


class LightEffect(Enum):
    """Enumeration of light effects."""

    FLASH = auto()
    PULSE = auto()
    RAINBOW = auto()
    STATIC = auto()


@dataclass
class LightConfig:
    """Configuration for light effects."""

    brightness: int = HueConfig.DEFAULT_BRIGHTNESS
    transition_time: int = 1
    effect: LightEffect = LightEffect.FLASH
    num_flashes: int = 3
    lights: list[str] = field(default_factory=list)
    color_timeout: int = HueConfig.COLOR_TIMEOUT


class HueController:
    """Controller for managing Hue lights on the bridge."""

    def __init__(self, bridge: Bridge, config: LightConfig | None = None) -> None:
        """Initialize the Hue Controller.

        Args:
            bridge: The Philips Hue bridge instance
            config: Optional light configuration settings
        """
        self.bridge: Bridge = bridge
        self.config: LightConfig = config or LightConfig()
        self._lights: list[int] = []
        self._update_lights()
        self._color_timer: asyncio.Task[None] | None = None
        self._last_state: dict[int, dict[str, Any]] = {}
        self._save_light_states()

    def _save_light_states(self) -> None:
        """Save the current state of all lights."""
        try:
            for light_id in self._lights:
                self._last_state[light_id] = self.bridge.get_light(light_id)
        except PhueException as e:
            logger.warning("Failed to save light states: %s", e)

    def _update_lights(self) -> None:
        """Update the list of available lights."""
        try:
            light_objects = self.bridge.get_light_objects()
            if isinstance(light_objects, list):
                self._lights = [
                    light.light_id
                    for light in light_objects
                    if not self.config.lights or light.name in self.config.lights
                ]
                if not self._lights:
                    logger.warning("No matching lights found on the Hue Bridge!")
            else:
                self._lights = []
                logger.warning("No lights found on the Hue Bridge!")
        except PhueException:
            logger.exception("Error updating lights!")
            self._lights = []

    async def _revert_lights(self, delay: float) -> None:
        """Revert lights to previous state after delay.

        Args:
            delay: Time in seconds to wait before reverting
        """
        await asyncio.sleep(delay)
        try:
            for light_id in self._lights:
                if light_id in self._last_state:
                    # Extract just the needed properties to restore
                    state = self._last_state[light_id]
                    restore_props = {
                        "on": state.get("state", {}).get("on", True),
                        "bri": state.get("state", {}).get("bri", HueConfig.DEFAULT_BRIGHTNESS),
                        "xy": state.get("state", {}).get("xy", HueConfig.COLOR_COMMANDS["white"]),
                    }
                    self.bridge.set_light(light_id, restore_props)
                else:
                    # Fallback to default if no saved state
                    self.bridge.set_light(light_id, HueConfig.DEFAULT_LIGHT_STATE)
            logger.info("Reverted lights to previous state")
        except PhueException as e:
            logger.warning("Error reverting lights: %s", e)

    async def set_color(self, color: str) -> None:
        """Set lights to specified color and schedule reversion.

        Args:
            color: The name of the color to set
        """
        if not self._lights:
            logger.warning("No lights found on the Hue Bridge!")
            return

        normalized_color = color.lower().strip()
        if normalized_color not in HueConfig.COLOR_COMMANDS:
            logger.warning("Invalid color specified: %s", color)
            return

        try:
            # Cancel existing timer if there is one
            if self._color_timer and not self._color_timer.done():
                self._color_timer.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._color_timer

            # Save current state if we haven't already
            if not self._last_state:
                self._save_light_states()

            # Set lights to specified color
            xy: list[float] = HueConfig.COLOR_COMMANDS[normalized_color]
            for light_id in self._lights:
                self.bridge.set_light(
                    light_id,
                    {
                        "on": True,
                        "bri": self.config.brightness,
                        "xy": xy,
                        "transitiontime": self.config.transition_time,
                    },
                )
            logger.info("Setting lights to %s", color)

            # Start new timer for reverting
            timeout = self.config.color_timeout
            self._color_timer = asyncio.create_task(self._revert_lights(delay=timeout))

        except PhueException as e:
            logger.warning("Error setting lights to %s: %s", color, e)

    async def flash_lights(self, color: str, num_flashes: int | None = None) -> None:
        """Flash lights a specific color.

        Args:
            color: The color to flash
            num_flashes: Number of times to flash (defaults to config setting)
        """
        if not self._lights:
            logger.warning("No lights found on the Hue Bridge!")
            return

        flashes = num_flashes or self.config.num_flashes
        normalized_color = color.lower().strip()

        if normalized_color not in HueConfig.COLOR_COMMANDS:
            logger.warning("Invalid color specified: %s", color)
            return

        try:
            # Save current state
            self._save_light_states()
            xy: list[float] = HueConfig.COLOR_COMMANDS[normalized_color]

            # Flash sequence
            for _ in range(flashes):
                # Turn on with color
                for light_id in self._lights:
                    self.bridge.set_light(
                        light_id,
                        {
                            "on": True,
                            "bri": self.config.brightness,
                            "xy": xy,
                            "transitiontime": 0,  # Instant change for flashing
                        },
                    )
                await asyncio.sleep(HueConfig.FLASH_DELAY)

                # Turn off briefly
                for light_id in self._lights:
                    self.bridge.set_light(light_id, {"on": False})
                await asyncio.sleep(HueConfig.FLASH_DELAY)

            # Restore original state
            await self._revert_lights(0)  # Immediate revert

        except PhueException as e:
            logger.warning("Error flashing lights: %s", e)


class EventHandler:
    """Event handler for processing Chaturbate events."""

    def __init__(self, hue_controller: HueController, config: ConfigManager) -> None:
        """Initialize the event handler.

        Args:
            hue_controller: The Hue controller instance
            config: Configuration manager for settings
        """
        self.hue: HueController = hue_controller
        self.config: ConfigManager = config

        # Load tip threshold from config or use default
        tip_threshold: str | None = self.config.get(key="TIP_THRESHOLD")
        self.tip_threshold: int = (
            int(tip_threshold) if tip_threshold else HueConfig.DEFAULT_REQUIRED_TOKENS
        )

        # Map of commands to handler methods
        self._commands: dict[str, Callable[..., Any]] = {
            "color": self._handle_color_command,
            "flash": self._handle_flash_command,
        }

        # Regular expressions for command parsing
        self._color_pattern: re.Pattern[str] = re.compile(
            r"(?:color|set|light)\s+(\w+)", re.IGNORECASE
        )
        self._flash_pattern: re.Pattern[str] = re.compile(
            r"flash\s+(\w+)(?:\s+(\d+))?", re.IGNORECASE
        )

    async def handle_event(self, event: Event) -> None:
        """Handle incoming events.

        Args:
            event: The event to handle
        """
        if isinstance(event.object.tip, Tip):
            await self.handle_tip(tip=event.object.tip)

    async def handle_tip(self, tip: Tip) -> None:
        """Handle incoming tip events.

        Args:
            tip: The tip event data
        """
        logger.info("Received tip of %d tokens", tip.tokens)

        # Only process tips that meet the threshold and have a message
        if tip.tokens >= self.tip_threshold and tip.message:
            message = tip.message.lower()

            # Check for color command
            color_match = self._color_pattern.search(message)
            if color_match:
                color_name = color_match.group(1)
                await self._handle_color_command(color_name)
                return

            # Check for flash command
            flash_match = self._flash_pattern.search(message)
            if flash_match:
                color_name = flash_match.group(1)
                count = int(flash_match.group(2)) if flash_match.group(2) else None
                await self._handle_flash_command(color_name, count)
                return

            # Direct color name in message
            for color in HueConfig.COLOR_COMMANDS:
                if color in message.split():
                    await self._handle_color_command(color)
                    break

    async def _handle_color_command(self, color: str) -> None:
        """Handle a color command.

        Args:
            color: The color to set
        """
        await self.hue.set_color(color)

    async def _handle_flash_command(self, color: str, count: int | None = None) -> None:
        """Handle a flash command.

        Args:
            color: The color to flash
            count: Number of flashes, if specified
        """
        await self.hue.flash_lights(color, count)


class EventMonitor:
    """Monitor Chaturbate events and control Hue lights."""

    def __init__(self, event_handler: EventHandler, client: ChaturbateClient) -> None:
        """Initialize the Event Monitor.

        Args:
            event_handler: The event handler for processing events
            client: The Chaturbate client
        """
        self.event_handler: EventHandler = event_handler
        self.client: ChaturbateClient = client
        self.running: bool = True

    async def monitor_events(self) -> None:
        """Monitor Chaturbate events with improved error handling."""
        url: str | None = None
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.running:
            try:
                response: EventsAPIResponse = await self.client.fetch_events(url)
                consecutive_errors = 0  # Reset error counter on success

                for event in response.events:
                    await self.event_handler.handle_event(event)
                url = response.next_url

            except asyncio.CancelledError:
                self.running = False
                break
            except Exception:
                consecutive_errors += 1
                logger.exception("Error monitoring events")

                # Exponential backoff with cap
                wait_time = min(2**consecutive_errors, 60)
                logger.info("Retrying in %d seconds...", wait_time)

                # If too many consecutive errors, take a longer break
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning("Too many consecutive errors, taking a longer break")
                    await asyncio.sleep(120)  # 2 minute break
                    consecutive_errors = 0  # Reset counter
                else:
                    await asyncio.sleep(wait_time)

    def stop(self) -> None:
        """Gracefully stop the monitor."""
        self.running = False


def setup_hue_bridge(ip_address: str, retries: int = HueConfig.CONNECTION_RETRIES) -> Bridge:
    """Setup and connect to the Hue Bridge.

    Args:
        ip_address: The IP address of the Hue Bridge
        retries: Number of connection attempts to make

    Returns:
        The connected Hue Bridge

    Raises:
        PhueException: If all connection attempts fail
    """
    logger.info("Connecting to Hue Bridge at %s", ip_address)

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            bridge: Bridge = Bridge(ip_address)
            bridge.connect()
            logger.info("Successfully connected to Hue Bridge")
        except PhueException as e:
            last_exception = e
            if attempt < retries:
                wait_time = HueConfig.RETRY_DELAY
                logger.warning(
                    "Connection attempt %d failed. Retrying in %d seconds...", attempt, wait_time
                )
                # Using sync sleep here as this is not in an async context
                time.sleep(wait_time)
        else:
            return bridge

    # If we get here, all retries failed
    logger.error("Failed to connect to Hue Bridge after %d attempts", retries)
    raise last_exception or PhueException(
        id="ConnectionError", message="Failed to connect to Hue Bridge"
    )


async def main() -> None:  # noqa: C901
    """Main application entry point.

    Raises:
        ValueError: If required configurations are missing.
    """
    config: ConfigManager = ConfigManager()

    # Validate required configuration
    username: str | None = config.get(key="CB_USERNAME")
    if not username:
        msg = "CB_USERNAME is required in the configuration"
        raise ValueError(msg)
    token: str | None = config.get(key="CB_TOKEN")
    if not token:
        msg = "CB_TOKEN is required in the configuration"
        raise ValueError(msg)

    # Setup Hue Bridge connection
    bridge_ip: str | None = config.get(key="HUE_IP", default=None)
    hue_ip: str = bridge_ip or HueConfig.DEFAULT_HUE_IP

    # Get light configuration
    light_config = LightConfig()
    light_names = config.get(key="LIGHT_NAMES", default="")
    if light_names:
        light_config.lights = [name.strip() for name in light_names.split(",") if name.strip()]
    brightness_value = config.get(key="BRIGHTNESS")
    if brightness_value and brightness_value.strip():
        try:
            light_config.brightness = int(brightness_value)
        except ValueError:
            logger.warning("Invalid BRIGHTNESS value '%s', using default", brightness_value)

    timeout_value = config.get(key="COLOR_TIMEOUT")
    if timeout_value and timeout_value.strip():
        try:
            light_config.color_timeout = int(timeout_value)
        except ValueError:
            logger.warning("Invalid COLOR_TIMEOUT value '%s', using default", timeout_value)

    # Log configuration
    logger.info("Using Hue Bridge IP: %s", hue_ip)
    logger.info(
        "Tip threshold: %s tokens",
        config.get(key="TIP_THRESHOLD") or HueConfig.DEFAULT_REQUIRED_TOKENS,
    )
    if light_config.lights:
        logger.info("Controlling specific lights: %s", ", ".join(light_config.lights))
    else:
        logger.info("Controlling all available lights")

    # Connect to bridge and setup controllers
    bridge: Bridge = setup_hue_bridge(ip_address=hue_ip)
    hue_controller: HueController = HueController(bridge, config=light_config)
    event_handler: EventHandler = EventHandler(hue_controller, config)

    # Test mode setting from config
    testbed_mode: bool = True
    testbed_value = config.get(key="TESTBED")
    if testbed_value and testbed_value.lower() in ("false", "no", "0"):
        testbed_mode = False

    logger.info("Starting in %s mode", "testbed" if testbed_mode else "production")
    async with ChaturbateClient(username, token, testbed=testbed_mode) as client:
        monitor: EventMonitor = EventMonitor(event_handler, client)
        try:
            await monitor.monitor_events()
        except asyncio.CancelledError:
            monitor.stop()
            logger.info("Shutting down gracefully...")


def run() -> None:
    """Run the application with comprehensive error handling."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except PhueException:
        logger.exception("Error communicating with Hue Bridge")
    except ValueError:
        logger.exception("Configuration error")
    except Exception:
        logger.exception("An unexpected error occurred")
    finally:
        logger.info("Exiting...")


if __name__ == "__main__":
    run()
