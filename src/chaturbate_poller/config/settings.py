"""Settings module for Chaturbate Poller."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from chaturbate_poller.constants import DEFAULT_BASE_URL, TESTBED_BASE_URL


class APISettings(BaseSettings):
    """Settings for the Chaturbate Events API."""

    username: str = Field(default=..., alias="API_USERNAME")
    token: str = Field(default=..., alias="API_TOKEN")
    timeout: int = Field(default=10, alias="API_TIMEOUT")
    testbed: bool = Field(default=False, alias="API_TESTBED")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="",  # Use explicit env names above
        validate_default=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any extra fields in the environment
    )


class InfluxDBSettings(BaseSettings):
    """Settings for InfluxDB integration."""

    url: str | None = Field(default=None, alias="INFLUXDB_URL")
    token: str | None = Field(default=None, alias="INFLUXDB_TOKEN")
    org: str | None = Field(default=None, alias="INFLUXDB_ORG")
    bucket: str | None = Field(default=None, alias="INFLUXDB_BUCKET")
    init_mode: str | None = Field(default=None, alias="INFLUXDB_INIT_MODE")
    init_username: str | None = Field(default=None, alias="INFLUXDB_INIT_USERNAME")
    init_password: str | None = Field(default=None, alias="INFLUXDB_INIT_PASSWORD")
    init_org: str | None = Field(default=None, alias="INFLUXDB_INIT_ORG")
    init_bucket: str | None = Field(default=None, alias="INFLUXDB_INIT_BUCKET")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="",
        validate_default=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore any extra fields in the environment
    )


class Settings(BaseSettings):
    """Consolidated application settings."""

    api: APISettings = APISettings()
    database: InfluxDBSettings = InfluxDBSettings()
    use_database: bool = Field(default=False, alias="USE_DATABASE")
    verbose: bool = Field(default=False, alias="VERBOSE")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=False,
    )

    @property
    def base_url(self) -> str:
        """Construct the appropriate base URL for the API."""
        template = TESTBED_BASE_URL if self.api.testbed else DEFAULT_BASE_URL
        return template.format(username=self.api.username, token=self.api.token)

    @property
    def write_url(self) -> str | None:
        """Construct the InfluxDB write URL."""
        if not self.database.url:
            return None
        base = str(self.database.url).rstrip("/")
        return (
            f"{base}/api/v2/write?org={self.database.org}&bucket={self.database.bucket}&precision=s"
        )
