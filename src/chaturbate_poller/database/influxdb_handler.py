"""Module to handle InfluxDB operations via HTTP API."""

import logging
from enum import Enum
from logging import Logger
from typing import TYPE_CHECKING, Any

import httpx

from chaturbate_poller.config.config_manager import ConfigManager
from chaturbate_poller.constants import HttpStatusCode

if TYPE_CHECKING:
    from httpx import Response

logger: Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""

type FieldValue = float | int | str | bool


class InfluxDBHandler:
    """Class to handle InfluxDB operations via HTTP API."""

    def __init__(self) -> None:
        """Initialize the InfluxDB handler by setting up configuration."""
        config_manager: ConfigManager = ConfigManager()

        self.url: str = config_manager.get(key="INFLUXDB_URL", default="").rstrip("/")
        self.token: str = config_manager.get(key="INFLUXDB_TOKEN", default="")
        self.org: str = config_manager.get(key="INFLUXDB_ORG", default="")
        self.bucket: str = config_manager.get(key="INFLUXDB_BUCKET", default="")

        self.write_url: str = (
            f"{self.url}/api/v2/write?org={self.org}&bucket={self.bucket}&precision=s"
        )
        self.headers: dict[str, str] = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "text/plain",
            "Accept": "application/json",
        }

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
            new_key: str = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                nested_dict: dict[str, Any] = v
                items.extend(
                    self.flatten_dict(data=nested_dict, parent_key=new_key, sep=sep).items()
                )
            elif isinstance(v, Enum):
                items.append((new_key, v.value))
            else:
                items.append((new_key, v))
        return dict(items)

    def format_line_protocol(self, measurement: str, data: dict[str, Any]) -> str:
        """Format the given data as InfluxDB Line Protocol.

        Args:
            measurement (str): The measurement name.
            data (dict[str, Any]): The event data to format.

        Returns:
            str: A properly formatted InfluxDB Line Protocol string.
        """
        fields: list[Any] = []
        for key, value in data.items():
            if isinstance(value, bool):
                fields.append(f"{key}={str(value).lower()}")  # pragma: no cover
            elif isinstance(value, int):
                fields.append(f"{key}={value}i")
            elif isinstance(value, float):
                fields.append(f"{key}={value}")  # pragma: no cover
            elif isinstance(value, str):
                escaped_value: str = value.replace('"', '"')
                fields.append(f'{key}="{escaped_value}"')

        return f"{measurement} {','.join(fields)}"

    def write_event(self, measurement: str, data: dict[str, Any]) -> None:
        """Write event data to InfluxDB via HTTP API.

        Args:
            measurement (str): The measurement name.
            data (dict[str, Any]): The event data to write.

        Raises:
            httpx.HTTPStatusError: If the request returns an HTTP error.
            httpx.RequestError: If a network error occurs.
        """
        flattened_data: dict[str, Any] = self.flatten_dict(data)
        line_protocol: str = self.format_line_protocol(measurement, data=flattened_data)

        try:
            response: Response = httpx.post(
                url=self.write_url, headers=self.headers, content=line_protocol
            )
            response.raise_for_status()
            if response.status_code == HttpStatusCode.NO_CONTENT:
                logger.debug("Data written to InfluxDB successfully")
            else:
                logger.error(  # pragma: no cover
                    "Failed to write data to InfluxDB: %s %s",
                    response.status_code,
                    response.text,
                )
        except httpx.HTTPStatusError as e:
            logger.exception(
                "HTTP error occurred while writing data to InfluxDB: %s", e.response.text
            )
            raise
        except httpx.RequestError:
            logger.exception("Network error occurred while writing data to InfluxDB")
            raise

    def close(self) -> None:
        """No-op method for compatibility with previous implementations."""
