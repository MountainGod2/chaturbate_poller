# ruff: noqa: S101
"""Tests for InfluxDBHandler."""

import logging

import pytest
from influxdb_client.rest import ApiException

from chaturbate_poller.influxdb_client import InfluxDBHandler


class TestInfluxDBHandler:
    """Tests for InfluxDBHandler."""

    def test_flatten_dict(self) -> None:
        """Test the dictionary flattening method."""
        handler = InfluxDBHandler()
        nested_dict = {"level1": {"level2": "value", "level2b": {"level3": "value3"}}}
        flattened_dict = handler.flatten_dict(nested_dict)
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
                {
                    "key": "value",
                    "nested": {"subkey": "subvalue", "subkey2": {"subsubkey": "value"}},
                },
                {"key": "value", "nested.subkey": "subvalue", "nested.subkey2.subsubkey": "value"},
            ),
        ],
    )
    def test_flatten_dict_with_params(self, input_dict: dict, expected_dict: dict) -> None:
        """Test flatten_dict method with various inputs."""
        handler = InfluxDBHandler()
        assert handler.flatten_dict(input_dict) == expected_dict

    def test_write_event(self, mocker) -> None:  # noqa: ANN001
        """Test writing an event to InfluxDB."""
        handler = InfluxDBHandler()
        mock_write_api = mocker.patch.object(handler.write_api, "write", autospec=True)
        event_data = {"event": "data"}
        handler.write_event("test_measurement", event_data)
        mock_write_api.assert_called_once()

    def test_write_event_failure(self, mocker, caplog) -> None:  # noqa: ANN001
        """Test writing an event to InfluxDB failure."""
        handler = InfluxDBHandler()
        mocker.patch.object(handler.write_api, "write", side_effect=ApiException)
        event_data = {"event": "data"}

        with caplog.at_level(logging.ERROR):
            handler.write_event("test_measurement", event_data)

        assert "Failed to write data to InfluxDB" in caplog.text

    def test_close_handler(self, mocker) -> None:  # noqa: ANN001
        """Test closing the InfluxDB handler."""
        handler = InfluxDBHandler()
        mock_close = mocker.patch.object(handler.client, "close", autospec=True)
        handler.close()
        mock_close.assert_called_once()
