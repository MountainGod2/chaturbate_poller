import os

import pytest
from pydantic import ValidationError

from chaturbate_poller.config.settings import APISettings, InfluxDBSettings, Settings


def test_api_settings_valid() -> None:
    """Test APISettings with valid environment variables."""
    settings = APISettings()
    assert settings.username == "test_user"
    assert settings.token == "test_token"  # noqa: S105
    assert settings.timeout == 15
    assert settings.testbed is True


def test_influxdb_settings_valid() -> None:
    """Test InfluxDBSettings with valid environment variables."""
    settings = InfluxDBSettings()
    assert settings.url == "http://localhost:8086"
    assert settings.token == "influx_token"  # noqa: S105
    assert settings.org == "test_org"
    assert settings.bucket == "test_bucket"


def test_settings_consolidated() -> None:
    """Test consolidated Settings class with valid environment variables."""
    settings = Settings()
    assert settings.api.username == "test_user"
    assert settings.api.token == "test_token"  # noqa: S105
    assert settings.api.timeout == 15
    assert settings.api.testbed is True
    assert settings.database.url == "http://localhost:8086"
    assert settings.database.token == "influx_token"  # noqa: S105
    assert settings.use_database is True
    assert settings.verbose is True


def test_base_url_property() -> None:
    """Test the base_url property of the Settings class."""
    settings = Settings()
    expected_url = "https://events.testbed.cb.dev/events/test_user/test_token/"
    assert settings.base_url == expected_url


def test_write_url_property() -> None:
    """Test the write_url property of the Settings class."""
    settings = Settings()
    expected_url = "http://localhost:8086/api/v2/write?org=test_org&bucket=test_bucket&precision=s"
    assert settings.write_url == expected_url


def test_invalid_api_settings() -> None:
    """Test APISettings with missing required fields."""
    os.environ.clear()
    with pytest.raises(ValidationError):
        APISettings()


def test_invalid_influxdb_settings() -> None:
    """Test InfluxDBSettings with missing required fields."""
    os.environ.clear()
    settings = InfluxDBSettings()
    assert settings.url is None
    assert settings.token is None
