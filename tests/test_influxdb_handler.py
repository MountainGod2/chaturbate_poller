# ruff: noqa: S101
"""Tests for InfluxDBHandler."""

import logging
import os
from unittest import mock

import pytest
from influxdb_client.rest import ApiException

from chaturbate_poller.influxdb_client import InfluxDBHandler


@pytest.fixture(scope="module")
def influxdb_handler() -> InfluxDBHandler:
    """Fixture for InfluxDBHandler."""
    return InfluxDBHandler()


def test_flatten_dict(influxdb_handler) -> None:  # noqa: ANN001
    """Test flatten_dict method."""
    nested_dict = {"level1": {"level2": "value", "level2b": {"level3": "value3"}}}
    flattened_dict = influxdb_handler.flatten_dict(nested_dict)
    expected_dict = {"level1.level2": "value", "level1.level2b.level3": "value3"}
    assert flattened_dict == expected_dict


@pytest.mark.parametrize(
    ("input_dict", "expected_dict"),
    [
        (
            {"key": "value", "nested": {"subkey": "subvalue"}},
            {"key": "value", "nested.subkey": "subvalue"},
        ),
        (
            {"key": "value", "nested": {"subkey": "subvalue", "subkey2": {"subsubkey": "value"}}},
            {"key": "value", "nested.subkey": "subvalue", "nested.subkey2.subsubkey": "value"},
        ),
    ],
)
def test_flatten_dict_with_params(influxdb_handler, input_dict, expected_dict) -> None:  # noqa: ANN001
    """Test flatten_dict method with different parameters."""
    assert influxdb_handler.flatten_dict(input_dict) == expected_dict


def test_write_event_success(influxdb_handler, mocker) -> None:  # noqa: ANN001
    """Test write_event method success."""
    mock_write_api = mocker.patch.object(influxdb_handler.write_api, "write", autospec=True)
    event_data = {"event": "data"}
    influxdb_handler.write_event("test_measurement", event_data)
    mock_write_api.assert_called_once()


def test_write_event_failure(influxdb_handler, mocker, caplog) -> None:  # noqa: ANN001
    """Test write_event method when write fails."""
    mocker.patch.object(influxdb_handler.write_api, "write", side_effect=ApiException)
    event_data = {"event": "data"}

    with caplog.at_level(logging.ERROR), pytest.raises(ApiException):
        influxdb_handler.write_event("test_measurement", event_data)

    assert "Failed to write data to InfluxDB" in caplog.text


def test_close_handler(influxdb_handler, mocker) -> None:  # noqa: ANN001
    """Test close method."""
    mock_close = mocker.patch.object(influxdb_handler.client, "close", autospec=True)
    influxdb_handler.close()
    mock_close.assert_called_once()


def test_influxdb_handler_init() -> None:
    """Test InfluxDBHandler initialization."""
    with mock.patch.dict(
        os.environ, {"INFLUXDB_URL": "http://localhost:8086", "INFLUXDB_TOKEN": "test_token"}
    ):
        handler = InfluxDBHandler()
        assert handler.client.url == "http://localhost:8086"
        assert handler.client.token == "test_token"  # noqa: S105
