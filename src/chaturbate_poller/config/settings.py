"""Application settings loaded from environment or a `.env` file, via Pydantic BaseSettings."""

from __future__ import annotations

from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration for chaturbate_poller, pulled from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        validate_default=False,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    cb_username: str
    cb_token: str

    influxdb_url: str | None = None
    influxdb_token: str | None = None
    influxdb_org: str | None = None
    influxdb_bucket: str | None = None
    use_database: bool = False

    influxdb_init_mode: str | None = None
    influxdb_init_username: str | None = None
    influxdb_init_password: str | None = None
    influxdb_init_org: str | None = None
    influxdb_init_bucket: str | None = None
