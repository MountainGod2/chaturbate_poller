import logging
import os
from socket import gaierror
from unittest import mock
from unittest.mock import Mock

import pytest
from influxdb_client.rest import ApiException
from urllib3.exceptions import NameResolutionError

from chaturbate_poller.influxdb_handler import InfluxDBHandler


class TestInfluxDBHandler:
    """Tests for the InfluxDBHandler class."""

    def test_handler_initialization(self) -> None:
        """Test successful initialization of InfluxDBHandler."""
        with mock.patch.dict(
            os.environ, {"INFLUXDB_URL": "http://localhost:8086", "INFLUXDB_TOKEN": "test_token"}
        ):
            handler = InfluxDBHandler()
            assert handler.client.url == "http://localhost:8086"
            assert handler.client.token == "test_token"  # noqa: S105

    def test_write_event_success(self, influxdb_handler: InfluxDBHandler, mocker: Mock) -> None:
        """Test successful event writing."""
        mock_write = mocker.patch.object(influxdb_handler.write_api, "write", autospec=True)
        influxdb_handler.write_event("test_measurement", {"event": "data"})
        mock_write.assert_called_once()

    def test_write_event_failure(
        self, influxdb_handler: InfluxDBHandler, mocker: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test event writing failure due to an API exception."""
        mocker.patch.object(influxdb_handler.write_api, "write", side_effect=ApiException)
        with pytest.raises(ApiException), caplog.at_level(logging.ERROR):
            influxdb_handler.write_event("test_measurement", {"event": "data"})
        assert "Error occurred while writing data to InfluxDB" in caplog.text

    def test_name_resolution_error(
        self, influxdb_handler: InfluxDBHandler, mocker: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test name resolution failure during event writing."""
        mock_conn = mock.Mock(spec=NameResolutionError.__bases__[0].__bases__[0])
        mocker.patch.object(
            influxdb_handler.write_api,
            "write",
            side_effect=NameResolutionError("host", mock_conn, mock.Mock(spec=gaierror)),
        )
        with pytest.raises(NameResolutionError), caplog.at_level(logging.ERROR):
            influxdb_handler.write_event("test_measurement", {"event": "data"})
        assert "Error occurred while writing data to InfluxDB" in caplog.text

    def test_close_handler(self, influxdb_handler: InfluxDBHandler, mocker: Mock) -> None:
        """Test proper closing of the handler."""
        mock_close = mocker.patch.object(influxdb_handler.client, "close", autospec=True)
        influxdb_handler.close()
        mock_close.assert_called_once()

    def test_flatten_dict_nested(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening of nested dictionaries."""
        nested_dict = {"a": {"b": {"c": 1}}, "d": 2}
        result = influxdb_handler.flatten_dict(nested_dict)
        assert result == {"a.b.c": 1, "d": 2}

    def test_flatten_dict_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening dictionary containing enum values."""
        from enum import Enum

        class TestEnum(Enum):
            VALUE1 = "test_value"
            VALUE2 = "test_value2"

        test_dict = {"enum_field": TestEnum.VALUE1, "normal_field": "test"}
        result = influxdb_handler.flatten_dict(test_dict)
        assert result == {"enum_field": "test_value", "normal_field": "test"}

    def test_flatten_dict_nested_with_enum(self, influxdb_handler: InfluxDBHandler) -> None:
        """Test flattening nested dictionary containing enum values."""
        from enum import Enum

        class TestEnum(Enum):
            VALUE1 = "test_value"

        test_dict = {"outer": {"inner": TestEnum.VALUE1}, "normal": "test"}
        result = influxdb_handler.flatten_dict(test_dict)
        assert result == {"outer.inner": "test_value", "normal": "test"}
