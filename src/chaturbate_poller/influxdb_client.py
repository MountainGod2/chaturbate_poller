"""Module to handle InfluxDB operations."""

import logging
import os
from enum import Enum
from typing import Any

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.rest import ApiException


class InfluxDBHandler:
    """Class to handle InfluxDB operations."""

    def __init__(self) -> None:
        """Initialize the InfluxDB handler."""
        load_dotenv(".env")
        self.url = os.getenv("INFLUXDB_URL", "")
        self.token = os.getenv("INFLUXDB_TOKEN", "")
        self.org = os.getenv("INFLUXDB_ORG", "")
        self.bucket = os.getenv("INFLUXDB_BUCKET", "")
        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.logger = logging.getLogger(__name__)

    def flatten_dict(
        self, data: dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> dict[str, Any]:
        """Flatten a nested dictionary and convert enums to strings.

        Args:
            data (dict[str, Any]): The dictionary to flatten.
            parent_key (str, optional): The base key string. Defaults to ''.
            sep (str, optional): The separator between keys. Defaults to '.'.

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
            data (dict[str, Any]): The event data.
        """
        try:
            flattened_data = self.flatten_dict(data)
            point = Point(measurement)
            for key, value in flattened_data.items():
                point = point.field(key, value)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            self.logger.info("Event data written to InfluxDB: %s", str(flattened_data))
        except ApiException:
            self.logger.exception("Failed to write data to InfluxDB")
            raise

    def close(self) -> None:
        """Close the InfluxDB client."""
        self.client.close()
