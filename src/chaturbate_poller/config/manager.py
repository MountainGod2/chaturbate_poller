"""Configuration manager module."""

from __future__ import annotations

import os
import pathlib
from typing import ClassVar

import dotenv


class ConfigManager:
    """Configuration manager for environment variables and .env files."""

    # Define all supported environment variables in one place
    ENV_VARIABLES: ClassVar[dict[str, str | bool]] = {
        "CB_USERNAME": "",
        "CB_TOKEN": "",
        "INFLUXDB_URL": "",
        "INFLUXDB_TOKEN": "",
        "INFLUXDB_ORG": "",
        "INFLUXDB_BUCKET": "",
        "USE_DATABASE": False,
        "INFLUXDB_INIT_MODE": "",
        "INFLUXDB_INIT_USERNAME": "",
        "INFLUXDB_INIT_PASSWORD": "",
        "INFLUXDB_INIT_ORG": "",
        "INFLUXDB_INIT_BUCKET": "",
    }

    def __init__(self, env_file: str = ".env") -> None:
        """Initialize the configuration manager.

        Args:
            env_file: The path to the environment file.
        """
        env_path: pathlib.Path = pathlib.Path(env_file)
        if env_path.exists():
            dotenv.load_dotenv(dotenv_path=env_path)
        self.config: dict[str, str | bool | None] = {}
        self._load_env_variables()

    @staticmethod
    def str_to_bool(value: str) -> bool:
        """Convert a string to a boolean value.

        Args:
            value: The string value to convert.

        Returns:
            The converted boolean value.
        """
        return value.lower() in {"true", "1", "yes"}

    def _load_env_variables(self) -> None:
        """Load environment variables and update the config dictionary."""
        for key, default_value in self.ENV_VARIABLES.items():
            env_value = os.getenv(key)
            if env_value is not None:
                if isinstance(default_value, bool):
                    self.config[key] = self.str_to_bool(env_value)
                else:
                    self.config[key] = env_value
            else:
                self.config[key] = default_value

    def get(self, key: str, default: str | None = None) -> str | None:
        """Retrieve a configuration value by key, or default value if the key is not found.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or default value.
        """
        value = self.config.get(key, default)
        if value is None:
            return default
        return str(value)

    def get_bool(self, key: str, *, default: bool = False) -> bool:
        """Retrieve a boolean configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The boolean configuration value or default value.
        """
        value = self.config.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return self.str_to_bool(value)
        return default
