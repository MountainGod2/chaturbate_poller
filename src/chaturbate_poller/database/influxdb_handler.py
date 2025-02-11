"""Module to handle InfluxDB operations."""

import logging
from enum import Enum
from typing import Any

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from influxdb_client.rest import ApiException
from urllib3.exceptions import NameResolutionError

from chaturbate_poller.config.manager import ConfigManager

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""

type FieldValue = float | int | str | bool


class InfluxDBHandler:
    """Class to handle InfluxDB operations."""

    client: InfluxDBClient
    write_api: WriteApi

    def __init__(self) -> None:
        """Initialize the InfluxDB handler by setting up the client and configuration."""
        config_manager = ConfigManager()

        self.url = config_manager.get("INFLUXDB_URL", "")
        self.token = config_manager.get("INFLUXDB_TOKEN", "")
        self.org = config_manager.get("INFLUXDB_ORG", "")
        self.bucket = config_manager.get("INFLUXDB_BUCKET", "")
        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def flatten_dict(
        self, data: dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> dict[str, Any]:
        """Flatten a nested dictionary and convert enums to strings.

        Args:
            data (dict[str, Any]): The dictionary to flatten.
            parent_key (str, optional): The base key string.
            sep (str, optional): The separator between keys.

        Returns:
            dict[str, Any]: The flattened dictionary.
        """
        items: list[tuple[str, Any]] = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, Enum):
                items.append((new_key, v.value))
            else:
                items.append((new_key, v))
        return dict(items)

    def write_event(self, measurement: str, data: dict[str, Any]) -> None:
        """Write event data to InfluxDB.

        Args:
            measurement (str): The measurement name.
            data (dict[str, Any]): The event data to write.

        Raises:
            ApiException: If an error occurs while writing the data.
            NameResolutionError: If a name resolution error occurs.
        """
        flattened_data = self.flatten_dict(data)
        point: Point = Point(measurement)  # type: ignore[no-untyped-call]
        for key, value in flattened_data.items():
            if isinstance(value, float | int | str | bool):
                point = point.field(key, value)  # type: ignore[no-untyped-call]
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.info("Event data written to InfluxDB: %s", str(flattened_data))
        except (ApiException, NameResolutionError):
            logger.exception("Error occurred while writing data to InfluxDB")
            raise

    def close(self) -> None:
        """Close the InfluxDB client."""
        self.client.close()  # type: ignore[no-untyped-call]
