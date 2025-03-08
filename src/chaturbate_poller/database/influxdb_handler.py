"""Module to handle InfluxDB operations via HTTP API."""

import logging
from enum import Enum
from logging import Logger
from typing import TYPE_CHECKING, TypedDict, cast

import httpx

from chaturbate_poller.config.config_manager import ConfigManager
from chaturbate_poller.constants import HttpStatusCode
from chaturbate_poller.database.nested_types import FieldValue, FlattenedDict, NestedDict

if TYPE_CHECKING:
    from httpx import Response

logger: Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


class InfluxData(TypedDict, total=False):
    """TypedDict for structured data that can be written to InfluxDB."""

    # This allows for any string keys with values that can be field values or nested dictionaries


class InfluxDBHandler:
    """Class to handle InfluxDB operations via HTTP API."""

    def __init__(self) -> None:
        """Initialize the InfluxDB handler by setting up configuration."""
        config_manager: ConfigManager = ConfigManager()

        url_value: str | None = config_manager.get(key="INFLUXDB_URL", default="")
        self.url: str = url_value.rstrip("/") if url_value is not None else ""
        self.token: str = config_manager.get(key="INFLUXDB_TOKEN", default="") or ""
        self.org: str = config_manager.get(key="INFLUXDB_ORG", default="") or ""
        self.bucket: str = config_manager.get(key="INFLUXDB_BUCKET", default="") or ""

        self.write_url: str = (
            f"{self.url}/api/v2/write?org={self.org}&bucket={self.bucket}&precision=s"
        )
        self.headers: dict[str, str] = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "text/plain",
            "Accept": "application/json",
        }

    def flatten_dict(self, data: NestedDict, parent_key: str = "", sep: str = ".") -> FlattenedDict:
        """Flatten a nested dictionary and convert enums to strings.

        Args:
            data: The dictionary to flatten.
            parent_key: The base key string.
            sep: The separator between keys.

        Returns:
            The flattened dictionary with only FieldValue values.
        """
        items: list[tuple[str, FieldValue]] = []
        for k, v in data.items():
            new_key: str = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                nested_dict: NestedDict = cast(NestedDict, v)
                items.extend(
                    self.flatten_dict(data=nested_dict, parent_key=new_key, sep=sep).items()
                )
            elif isinstance(v, Enum):
                items.append((new_key, v.value))
            else:
                field_value: FieldValue = v
                items.append((new_key, field_value))
        return dict(items)

    def format_line_protocol(self, measurement: str, data: FlattenedDict) -> str:
        """Format the given data as InfluxDB Line Protocol.

        Args:
            measurement: The measurement name.
            data: The flattened event data to format.

        Returns:
            A properly formatted InfluxDB Line Protocol string.
        """
        fields: list[str] = []
        for key, value in data.items():
            if isinstance(value, bool):
                fields.append(f"{key}={str(value).lower()}")  # pragma: no cover
            elif isinstance(value, int):  # pragma: no cover
                fields.append(f"{key}={value}i")
            elif isinstance(value, float):
                fields.append(f"{key}={value}")  # pragma: no cover
            elif hasattr(value, "replace"):  # Check if it's a string or string-like object
                # Escape double quotes in string values
                escaped_value: str = value.replace('"', '"')
                fields.append(f'{key}="{escaped_value}"')
            # Skip other types that are not valid for InfluxDB line protocol

        return f"{measurement} {','.join(fields)}"

    def write_event(self, measurement: str, data: NestedDict) -> None:
        """Write event data to InfluxDB via HTTP API.

        Args:
            measurement: The measurement name.
            data: The event data to write.

        Raises:
            httpx.HTTPStatusError: If the request returns an HTTP error.
            httpx.RequestError: If a network error occurs.
        """
        try:
            flattened_data: FlattenedDict = self.flatten_dict(data)
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
        except (TypeError, ValueError):  # pragma: no cover
            logger.exception("Error processing data for InfluxDB")
            raise

    def close(self) -> None:
        """No-op method for compatibility with previous implementations."""
