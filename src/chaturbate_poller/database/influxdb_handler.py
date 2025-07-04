"""Module to handle InfluxDB operations via HTTP API."""

from __future__ import annotations

import enum
import logging
import typing

import httpx

from chaturbate_poller.config.manager import ConfigManager
from chaturbate_poller.constants import HttpStatusCode

if typing.TYPE_CHECKING:
    from chaturbate_poller.database.nested_types import FieldValue, FlattenedDict, NestedDict

logger = logging.getLogger(__name__)


class InfluxData(typing.TypedDict, total=False):
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
        """Flatten a nested dictionary and convert enums to strings."""
        items: list[tuple[str, FieldValue]] = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                nested_dict: NestedDict = typing.cast("NestedDict", v)
                items.extend(
                    self.flatten_dict(data=nested_dict, parent_key=new_key, sep=sep).items()
                )
            elif isinstance(v, enum.Enum):
                items.append((new_key, v.value))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def _format_field(key: str, value: FieldValue) -> str:
        """Format a single field for InfluxDB line protocol."""
        if isinstance(value, bool):
            return f"{key}={str(value).lower()}"
        if isinstance(value, int):
            return f"{key}={value}i"
        if isinstance(value, float):
            return f"{key}={value}"

        # String values - escape double quotes
        escaped_value = str(value).replace('"', '\\"')
        return f'{key}="{escaped_value}"'

    def format_line_protocol(self, measurement: str, data: FlattenedDict) -> str:
        """Format the given data as InfluxDB Line Protocol.

        Args:
            measurement: The measurement name.
            data: The flattened event data to format.

        Returns:
            A properly formatted InfluxDB Line Protocol string.
        """
        fields = [self._format_field(key, value) for key, value in data.items()]
        return f"{measurement} {','.join(fields)}"

    def write_event(self, measurement: str, data: NestedDict) -> None:
        """Write event data to InfluxDB via HTTP API.

        Args:
            measurement: The measurement name.
            data: The event data to write.

        Raises:
            httpx.HTTPStatusError: If the request returns an HTTP error.
            httpx.RequestError: If a network error occurs.
            ValueError: If data cannot be processed for InfluxDB.
        """
        try:
            flattened_data: FlattenedDict = self.flatten_dict(data)
            line_protocol: str = self.format_line_protocol(measurement, data=flattened_data)
        except (TypeError, ValueError) as e:
            logger.exception("Error processing data for InfluxDB")
            msg = "Unable to process data for InfluxDB format"
            raise ValueError(msg) from e

        try:
            response: httpx.Response = httpx.post(
                url=self.write_url, headers=self.headers, content=line_protocol
            )
            response.raise_for_status()
            if response.status_code == HttpStatusCode.NO_CONTENT:
                logger.debug("Data written to InfluxDB successfully")
            else:
                logger.error(
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
