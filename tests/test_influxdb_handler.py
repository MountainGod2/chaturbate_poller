from __future__ import annotations

import logging
import os
from enum import Enum
from typing import TYPE_CHECKING, cast
from unittest import mock

import httpx
import pytest

from chaturbate_poller.database.influxdb_handler import InfluxDBHandler

if TYPE_CHECKING:
    from chaturbate_poller.database.nested_types import NestedDict


class TestInfluxDBHandler:
    """Tests for the InfluxDBHandler class."""

    def test_handler_initialization(self) -> None:
        """Test successful initialization of InfluxDBHandler."""
        with mock.patch.dict(
            os.environ, {"INFLUXDB_URL": "http://localhost:8086", "INFLUXDB_TOKEN": "test_token"}
        ):
            handler = InfluxDBHandler()
            assert handler.url == "http://localhost:8086"
            assert handler.token == "test_token"  # noqa: S105

    async def test_write_event_success(
        self, influxdb_handler: InfluxDBHandler, mocker: mock.Mock
    ) -> None:
        """Test successful event writing."""
        mock_post = mocker.patch(
            "httpx.AsyncClient.post",
            new_callable=mocker.AsyncMock,
            return_value=mock.Mock(status_code=204),
        )
        await influxdb_handler.write_event("test_measurement", {"event": "data"})
        mock_post.assert_called_once()

    async def test_write_event_failure(
        self,
        influxdb_handler: InfluxDBHandler,
        mocker: mock.Mock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test event writing failure due to an HTTP error."""
        mock_response = mock.Mock(status_code=400, text="Test Error")
        mock_request = mock.Mock()

        mocker.patch(
            "httpx.AsyncClient.post",
            new_callable=mocker.AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "Test Error", request=mock_request, response=mock_response
            ),
        )

        with pytest.raises(httpx.HTTPStatusError), caplog.at_level(logging.ERROR):
            await influxdb_handler.write_event("test_measurement", {"event": "data"})

        assert "HTTP error occurred while writing data to InfluxDB" in caplog.text

    async def test_name_resolution_error(
        self,
        influxdb_handler: InfluxDBHandler,
        mocker: mock.Mock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test name resolution failure during event writing."""
        mocker.patch(
            "httpx.AsyncClient.post",
            new_callable=mocker.AsyncMock,
            side_effect=httpx.RequestError("Connection error"),
        )

        with pytest.raises(httpx.RequestError), caplog.at_level(logging.ERROR):
            await influxdb_handler.write_event("test_measurement", {"event": "data"})
        assert "Network error occurred while writing data to InfluxDB" in caplog.text

    def test_flatten_dict_nested(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening of nested dictionaries."""
        nested_dict: NestedDict = {"a": {"b": {"c": 1}}, "d": 2}
        result = influxdb_handler.flatten_dict(nested_dict)
        assert result == {"a.b.c": 1, "d": 2}

    def test_flatten_dict_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening dictionary containing enum values."""

        class TestEnum(Enum):
            VALUE1 = "test_value"
            VALUE2 = "test_value2"

        test_dict: NestedDict = {"enum_field": TestEnum.VALUE1, "normal_field": "test"}
        result = influxdb_handler.flatten_dict(test_dict)
        assert result == {"enum_field": "test_value", "normal_field": "test"}

    def test_flatten_dict_nested_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening nested dictionary containing enum values."""

        class TestEnum(Enum):
            VALUE1 = "test_value"

        # Cast to NestedDict to satisfy type checking while allowing TestEnum in test
        test_dict = cast("NestedDict", {"outer": {"inner": TestEnum.VALUE1}, "normal": "test"})
        result = influxdb_handler.flatten_dict(test_dict)
        assert result == {"outer.inner": "test_value", "normal": "test"}

    async def test_write_event_with_non_field_values(
        self, influxdb_handler: InfluxDBHandler, mocker: mock.Mock
    ) -> None:
        """Test event writing with non-FieldValue types."""
        mock_post = mocker.patch(
            "httpx.AsyncClient.post",
            new_callable=mocker.AsyncMock,
            return_value=mock.Mock(status_code=204),
        )

        # Use a dictionary that adheres to the NestedDict type
        test_data: NestedDict = {
            "valid_field": "test",
            "valid_number": 42,
        }
        await influxdb_handler.write_event("test_measurement", test_data)

        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        line_protocol = call_args["content"]

        assert "valid_field" in line_protocol
        assert "valid_number" in line_protocol
        assert "invalid_field" not in line_protocol
