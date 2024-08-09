# ruff: noqa: S101
"""Tests for InfluxDBHandler."""

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
