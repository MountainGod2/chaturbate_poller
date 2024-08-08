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

    def format_data_for_storage(self, data: dict[str, Any]) -> dict[str, Any]:
        """Format data for InfluxDB storage with user-friendly structure.

        Args:
            data (dict[str, Any]): The data to format.

        Returns:
            dict[str, Any]: The formatted data.
        """
        return {
            "timestamp": data.get("timestamp"),
            "event_type": data.get("event_type"),
            "user": {
                "username": data.get("user", {}).get("username", ""),
                "broadcaster": data.get("user", {}).get("broadcaster", ""),
                "in_fanclub": data.get("user", {}).get("in_fanclub", False),
                "has_tokens": data.get("user", {}).get("has_tokens", False),
                "is_mod": data.get("user", {}).get("is_mod", False),
                "recent_tips": data.get("user", {}).get("recent_tips", ""),
                "gender": data.get("user", {}).get("gender", ""),
                "subgender": data.get("user", {}).get("subgender", ""),
            },
            "media": data.get("media"),
            "tip": data.get("tip"),
            "message": data.get("message"),
            "subject": data.get("subject"),
            "event_id": data.get("event_id"),
        }

    def write_event(self, measurement: str, data: dict[str, Any]) -> None:
        """Write event data to InfluxDB.

        Args:
            measurement (str): The measurement name.
            data (dict[str, Any]): The event data.
        """
        try:
            formatted_data = self.format_data_for_storage(data)
            flattened_data = self.flatten_dict(formatted_data)
            point = Point(measurement)
            for key, value in flattened_data.items():
                point = point.field(key, value)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            self.logger.info("Event data written to InfluxDB: %s", flattened_data)
        except ApiException:
            self.logger.exception("Failed to write data to InfluxDB")

    def close(self) -> None:
        """Close the InfluxDB client."""
        self.client.close()
