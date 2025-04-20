# /// script
# dependencies = [
#   "chaturbate-poller==2.2.3",
#   "phue==1.1",
# ]
# requires-python = ">=3.12"
# ///

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, NotRequired, TypedDict

from phue import Bridge, PhueException
from rich.logging import RichHandler

from chaturbate_poller import ChaturbateClient, ConfigManager
from chaturbate_poller.exceptions import AuthenticationError
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.tip import Tip

if TYPE_CHECKING:
    from chaturbate_poller.models.api_response import EventsAPIResponse
import rich_click as click

# -------------------------------
# Constants and Configuration
# -------------------------------


click.rich_click.MAX_WIDTH = 100


@dataclass(frozen=True)
class HueConfig:
    """Configuration for Hue light commands."""

    DEFAULT_HUE_IP: ClassVar[str] = "192.168.0.23"
    FLASH_DELAY: ClassVar[float] = 0.5
    DEFAULT_REQUIRED_TOKENS: ClassVar[int] = 35
    COLOR_TIMEOUT: ClassVar[int] = 600  # 10 minutes in seconds
    DEFAULT_BRIGHTNESS: ClassVar[int] = 254

    COLOR_COMMANDS: ClassVar[dict[str, list[float]]] = {
        "red": [0.6750, 0.3220],
        "orange": [0.6000, 0.3600],
        "yellow": [0.5, 0.4],
        "green": [0.2151, 0.7106],
        "blue": [0.1538, 0.0600],
        "indigo": [0.2000, 0.1000],
        "violet": [0.2651, 0.1241],
        "white": [0.3227, 0.3290],
    }

    DEFAULT_LIGHT_STATE: ClassVar[dict[str, bool | int | list[float]]] = {
        "on": True,
        "bri": DEFAULT_BRIGHTNESS,
        "xy": COLOR_COMMANDS["white"],
        "transitiontime": 1,
    }

    CONNECTION_RETRIES: ClassVar[int] = 3
    RETRY_DELAY: ClassVar[int] = 5  # seconds


@dataclass
class LightConfig:
    """Configuration for light effects."""

    brightness: int = HueConfig.DEFAULT_BRIGHTNESS
    transition_time: int = 1
    num_flashes: int = 3
    lights: list[str] = field(default_factory=list)
    color_timeout: int = HueConfig.COLOR_TIMEOUT


# -------------------------------
# Logging Configuration
# -------------------------------


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("phue").setLevel(logging.WARNING)


logger = logging.getLogger("hue_light_control")

logger.info("Starting Hue Light Control script")

# -------------------------------
# Utility: Hue Bridge Connection
# -------------------------------


def setup_hue_bridge(ip_address: str, retries: int = HueConfig.CONNECTION_RETRIES) -> Bridge:
    """Setup and connect to the Hue Bridge."""
    logger.info("Connecting to Hue Bridge at %s", ip_address)
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            bridge: Bridge = Bridge(ip_address)
            if not bridge.get_api():
                bridge.connect()
            logger.info("Successfully connected to Hue Bridge")
        except PhueException as e:
            last_exception = e
            if attempt < retries:
                logger.warning(
                    "Connection attempt %d failed. Retrying in %d seconds...",
                    attempt,
                    HueConfig.RETRY_DELAY,
                )
                time.sleep(HueConfig.RETRY_DELAY)
        else:
            return bridge

    logger.error("Failed to connect to Hue Bridge after %d attempts", retries)
    raise last_exception or PhueException(
        id="ConnectionError", message="Unable to connect to Hue Bridge"
    )


# -------------------------------
# Hue Light Control
# -------------------------------


class HueLightInnerState(TypedDict):
    """TypedDict representing the inner 'state' dictionary of a Hue light."""

    on: bool
    bri: int
    xy: list[float]
    transitiontime: NotRequired[int]


class HueLightState(TypedDict):
    """TypedDict representing the full state of a Hue light."""

    state: HueLightInnerState
    name: str
    type: str
    modelid: NotRequired[str]
    swversion: NotRequired[str]


class HueController:
    """Controller for managing Philips Hue lights."""

    def __init__(self, bridge: Bridge, config: LightConfig | None = None) -> None:
        """Initialize the HueController with a bridge and configuration."""
        self.bridge: Bridge = bridge
        self.config: LightConfig = config or LightConfig()
        self._lights: list[int] = []
        self._last_state: dict[int, HueLightState] = {}
        self._color_timer: asyncio.Task[None] | None = None

        self._update_lights()
        self._save_light_states()

    def _update_lights(self) -> None:
        """Update available lights based on config."""
        try:
            light_objects = self.bridge.get_light_objects() or []
            self._lights = [
                light.light_id
                for light in light_objects
                if not self.config.lights or light.name in self.config.lights
            ]
            logger.info("Found %d matching lights", len(self._lights))
            if not self._lights:
                logger.warning("No matching lights found on the Hue Bridge!")
        except PhueException:
            self._lights = []
            logger.exception("Error retrieving lights from bridge")

    def _save_light_states(self) -> None:
        """Save current state of lights for restoration."""
        try:
            for light_id in self._lights:
                light_state = self.bridge.get_light(light_id)
                self._last_state[light_id] = light_state
        except PhueException:
            logger.warning("Unable to save light state")

    async def _revert_lights(self, delay: float) -> None:
        """Revert lights after a delay."""
        await asyncio.sleep(delay)
        try:
            for light_id in self._lights:
                state: HueLightState | dict[Any, Any] = self._last_state.get(light_id, {})
                props: HueLightInnerState | Any = state.get("state", {})
                self.bridge.set_light(
                    light_id,
                    parameter={
                        "on": props.get("on", True),
                        "bri": props.get("bri", HueConfig.DEFAULT_BRIGHTNESS),
                        "xy": props.get("xy", HueConfig.COLOR_COMMANDS["white"]),
                    },
                )
            logger.info("Reverted lights to original state")
        except PhueException:
            logger.warning("Failed to revert lights")

    async def set_color(self, color: str) -> None:
        """Set lights to a color and schedule reversion."""
        if not self._lights:
            logger.warning("No lights available")
            return

        normalized = color.strip().lower()
        xy: list[float] | None = HueConfig.COLOR_COMMANDS.get(normalized)
        if not xy:
            logger.warning("Unknown color: %s", color)
            return

        if self._color_timer:
            self._color_timer.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._color_timer

        self._save_light_states()
        for light_id in self._lights:
            self.bridge.set_light(
                light_id,
                parameter={
                    "on": True,
                    "bri": self.config.brightness,
                    "xy": xy,
                    "transitiontime": self.config.transition_time,
                },
            )
        logger.info("Lights set to %s", color)

        self._color_timer = asyncio.create_task(self._revert_lights(HueConfig.COLOR_TIMEOUT))

    async def flash_lights(self, color: str, count: int | None = None) -> None:
        """Flash lights in a specific color."""
        if not self._lights:
            logger.warning("No lights available to flash")
            return

        normalized: str = color.strip().lower()
        xy: list[float] | None = HueConfig.COLOR_COMMANDS.get(normalized)
        if not xy:
            logger.warning("Unknown color for flash: %s", color)
            return

        flashes: int = count or self.config.num_flashes
        self._save_light_states()

        try:
            for _ in range(flashes):
                for light_id in self._lights:
                    self.bridge.set_light(
                        light_id,
                        parameter={
                            "on": True,
                            "bri": self.config.brightness,
                            "xy": xy,
                            "transitiontime": 0,
                        },
                    )
                await asyncio.sleep(HueConfig.FLASH_DELAY)
                for light_id in self._lights:
                    self.bridge.set_light(light_id, parameter={"on": False})
                await asyncio.sleep(HueConfig.FLASH_DELAY)
        finally:
            await self._revert_lights(delay=0)


# -------------------------------
# Event Handlers
# -------------------------------


class EventHandler:
    """Handles incoming Chaturbate events."""

    def __init__(self, hue_controller: HueController, config: ConfigManager) -> None:
        """Initialize the event handler."""
        self.hue: HueController = hue_controller
        self.config: ConfigManager = config
        self.tip_threshold: int = int(
            config.get(key="TIP_THRESHOLD") or HueConfig.DEFAULT_REQUIRED_TOKENS
        )

    async def handle_event(self, event: Event) -> None:
        """Handle Chaturbate events."""
        if isinstance(event.object.tip, Tip):
            await self.handle_tip(event.object.tip)

    async def handle_tip(self, tip: Tip) -> None:
        """Handle a tip."""
        logger.info("Received tip: %d tokens", tip.tokens)
        if tip.tokens < self.tip_threshold or not tip.message:
            return

        message = tip.message.lower()

        for color in HueConfig.COLOR_COMMANDS:
            if color in message.split():
                await self.hue.set_color(color)
                break


class EventMonitor:
    """Monitors Chaturbate events."""

    def __init__(self, handler: EventHandler, client: ChaturbateClient) -> None:
        """Initialize the event monitor."""
        self.handler: EventHandler = handler
        self.client: ChaturbateClient = client
        self.running: bool = True

    async def monitor_events(self) -> None:
        """Main monitoring loop."""
        url: str | None = None
        consecutive_errors = 0
        max_errors = 5

        while self.running:
            try:
                response: EventsAPIResponse = await self.client.fetch_events(url)
                for event in response.events:
                    await self.handler.handle_event(event)
                url = response.next_url
                consecutive_errors = 0
            except asyncio.CancelledError:
                self.running = False
                break
            except AuthenticationError:
                logger.exception("Authentication error. Check your credentials.")
                break
            except Exception:
                logger.exception("Failed during event monitoring")
                consecutive_errors += 1
                wait = min(2**consecutive_errors, 60)
                logger.info("Retrying in %d seconds...", wait)
                if consecutive_errors >= max_errors:
                    logger.warning("Too many consecutive errors, waiting 2 minutes")
                    await asyncio.sleep(120)
                    consecutive_errors = 0
                else:
                    await asyncio.sleep(wait)

    def stop(self) -> None:
        """Stop monitoring."""
        self.running = False


# -------------------------------
# Entry Point
# -------------------------------


async def main(*, testbed: bool) -> None:
    """Main async entry."""
    config: ConfigManager = ConfigManager()

    username: str | None = config.get(key="CB_USERNAME")
    token: str | None = config.get(key="CB_TOKEN")
    if not username or not token:
        msg = "CB_USERNAME and CB_TOKEN must be configured"
        raise ValueError(msg)

    hue_ip: str = config.get(key="HUE_IP") or HueConfig.DEFAULT_HUE_IP
    light_names: str | None = config.get(key="LIGHT_NAMES", default="")
    brightness: str | None = config.get(key="BRIGHTNESS", default=None)
    timeout: str | None = config.get(key="COLOR_TIMEOUT", default=None)

    light_config: LightConfig = LightConfig()
    if light_names:
        light_config.lights = [n.strip() for n in light_names.split(sep=",") if n.strip()]
    if brightness and brightness.isdigit():
        light_config.brightness = int(brightness)
    if timeout and timeout.isdigit():
        light_config.color_timeout = int(timeout)

    logger.info("Hue Bridge IP: %s", hue_ip)
    logger.info(
        "Light targets: %s", ", ".join(light_config.lights) if light_config.lights else "all"
    )

    bridge: Bridge = setup_hue_bridge(ip_address=hue_ip)
    hue_controller: HueController = HueController(bridge, config=light_config)
    handler: EventHandler = EventHandler(hue_controller, config)

    async with ChaturbateClient(username, token, testbed=testbed) as client:
        monitor: EventMonitor = EventMonitor(handler, client)
        try:
            await monitor.monitor_events()
        except asyncio.CancelledError:
            monitor.stop()
            logger.info("Shutdown received...")


@click.command()
@click.option("--testbed", is_flag=True, help="Use Chaturbate testbed")
def cli(*, testbed: bool) -> None:
    """Run the Hue integration."""
    setup_logging()
    try:
        asyncio.run(main(testbed=testbed))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception:
        logger.exception("Fatal error occurred")
    finally:
        logger.info("Hue Light Control script terminated")


if __name__ == "__main__":
    cli()
