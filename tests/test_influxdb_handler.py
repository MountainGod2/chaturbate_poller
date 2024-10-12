import logging
import os
from enum import Enum
from typing import Any

import pytest
from influxdb_client.rest import ApiException
from urllib3.exceptions import NameResolutionError

from chaturbate_poller.influxdb_handler import InfluxDBHandler


class TestEnum(Enum):
    """Example enum for testing."""

    __test__ = False
    EXAMPLE = "example_value"


class TestInfluxDBClient:
    """Tests for the InfluxDBClient class."""

    @pytest.mark.parametrize(
        ("nested_dict", "expected_dict"),
        [
            (
                {"level1": {"level2": "value", "level2b": {"level3": "value3"}}},
                {"level1.level2": "value", "level1.level2b.level3": "value3"},
            ),
            (
                {
                    "key": "value",
                    "nested": {"subkey": "subvalue", "subkey2": {"subsubkey": "value"}},
                },
                {"key": "value", "nested.subkey": "subvalue", "nested.subkey2.subsubkey": "value"},
            ),
        ],
    )
    def test_flatten_dict_with_params(
        self, influxdb_handler: InfluxDBHandler, nested_dict: dict, expected_dict: dict
    ) -> None:
        """Test flatten_dict method with different parameters."""
        assert influxdb_handler.flatten_dict(nested_dict) == expected_dict

    def test_flatten_dict_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flatten_dict method with an enum value."""
        nested_dict = {"level1": {"enum_field": TestEnum.EXAMPLE, "other_field": "value"}}
        flattened_dict = influxdb_handler.flatten_dict(nested_dict)
        expected_dict = {"level1.enum_field": "example_value", "level1.other_field": "value"}
        assert flattened_dict == expected_dict

    def test_write_event_success(self, influxdb_handler: InfluxDBHandler, mocker: Any) -> None:
        """Test write_event method success."""
        mock_write_api = mocker.patch.object(influxdb_handler.write_api, "write", autospec=True)
        event_data = {"event": "data"}
        influxdb_handler.write_event("test_measurement", event_data)
        mock_write_api.assert_called_once()

    def test_write_event_failure(
        self, influxdb_handler: InfluxDBHandler, mocker: Any, caplog: Any
    ) -> None:
        """Test write_event method when write fails."""
        mocker.patch.object(influxdb_handler.write_api, "write", side_effect=ApiException)
        event_data = {"event": "data"}
        with caplog.at_level(logging.ERROR), pytest.raises(ApiException):
            influxdb_handler.write_event("test_measurement", event_data)
        assert "Error occurred while writing data to InfluxDB" in caplog.text

    def test_name_resolution_error(
        self, influxdb_handler: InfluxDBHandler, mocker: Any, caplog: Any
    ) -> None:
        """Test write_event method when name resolution fails."""
        mocker.patch.object(
            influxdb_handler.write_api,
            "write",
            side_effect=NameResolutionError(host="influxdb", conn=None, reason=None),  # type: ignore[arg-type]
        )
        event_data = {"event": "data"}
        with caplog.at_level(logging.ERROR), pytest.raises(NameResolutionError):
            influxdb_handler.write_event("test_measurement", event_data)

        assert "Error occurred while writing data to InfluxDB" in caplog.text

    def test_close_handler(self, influxdb_handler: InfluxDBHandler, mocker: Any) -> None:
        """Test close method."""
        mock_close = mocker.patch.object(influxdb_handler.client, "close", autospec=True)
        influxdb_handler.close()
        mock_close.assert_called_once()

    def test_influxdb_handler_init(self, mocker: Any) -> None:
        """Test InfluxDBHandler initialization."""
        mocker.patch.dict(
            os.environ, {"INFLUXDB_URL": "http://localhost:8086", "INFLUXDB_TOKEN": "test_token"}
        )
        handler = InfluxDBHandler()
        assert handler.client.url == "http://localhost:8086"
        assert handler.client.token == "test_token"  # noqa: S105
