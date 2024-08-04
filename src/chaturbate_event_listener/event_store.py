"""Event store module.

This module contains the EventStore class responsible for storing events.
"""

from abc import ABC, abstractmethod

from influxdb_client import InfluxDBClient, Point, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.models import Event


class EventStore(ABC):
    """Event store abstract base class."""

    @abstractmethod
    def store_event(self, event: Event) -> None:
        """Store an event.

        Args:
            event (Event): The event to store.
        """
        pass  # noqa: PIE790


class ConsoleEventStore(EventStore):
    """Console event store class."""

    def store_event(self, event: Event) -> None:
        """Store an event.

        Args:
            event (Event): The event to store.
        """
        print(f"Event: {event}")  # noqa: T201


class InfluxDBEventStore(EventStore):
    """InfluxDB event store class."""

    def __init__(self, config: Config) -> None:
        """Initialize the InfluxDBEventStore.

        Args:
            config (Config): The configuration.
        """
        self.client = InfluxDBClient(
            url=config.influxdb_url, token=config.influxdb_token, org=config.influxdb_org
        )
        self.write_api: WriteApi = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = config.influxdb_bucket

    def _flatten_dict(self, data: dict, parent_key: str = "", sep: str = "_") -> dict:
        items: list[tuple[str, str]] = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def store_event(self, event: Event) -> None:
        """Store an event.

        Args:
            event (Event): The event to store.
        """
        flattened_data = self._flatten_dict(event.to_dict())
        point = Point("event").tag("type", event.method)
        for key, value in flattened_data.items():
            point = point.field(key, value)
        self.write_api.write(bucket=self.bucket, org=self.client.org, record=point)


def get_event_store(config: Config) -> EventStore:
    """Get an event store.

    Args:
        config (Config): The configuration.

    Returns:
        EventStore: An event store.
    """
    if config.event_store_type == "influxdb":
        return InfluxDBEventStore(config)
    return ConsoleEventStore()
