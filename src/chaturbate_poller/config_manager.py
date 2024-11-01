"""Centralized configuration module."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class ConfigManager:
    """Centralized configuration manager."""

    def __init__(self, env_file: str = ".env") -> None:
        """Initialize the configuration manager.

        Args:
            env_file (str): The path to the environment file.
        """
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        self.config: dict[str, Any] = {}
        self.load_env_variables()

    @staticmethod
    def str_to_bool(value: str) -> bool:
        """Convert a string to a boolean value.

        Args:
            value (str): The string value to convert.

        Returns:
            bool: The converted boolean value.
        """
        return value.lower() in ["true", "1", "yes"]

    def load_env_variables(self) -> None:
        """Load environment variables and update the config dictionary."""
        env_config = {
            "CB_USERNAME": os.getenv("CB_USERNAME"),
            "CB_TOKEN": os.getenv("CB_TOKEN"),
            "INFLUXDB_URL": os.getenv("INFLUXDB_URL"),
            "INFLUXDB_TOKEN": os.getenv("INFLUXDB_TOKEN"),
            "INFLUXDB_ORG": os.getenv("INFLUXDB_ORG"),
            "INFLUXDB_BUCKET": os.getenv("INFLUXDB_BUCKET"),
            "USE_DATABASE": self.str_to_bool(os.getenv("USE_DATABASE", "false")),
            "INFLUXDB_INIT_MODE": os.getenv("INFLUXDB_INIT_MODE"),
            "INFLUXDB_INIT_USERNAME": os.getenv("INFLUXDB_INIT_USERNAME"),
            "INFLUXDB_INIT_PASSWORD": os.getenv("INFLUXDB_INIT_PASSWORD"),
            "INFLUXDB_INIT_ORG": os.getenv("INFLUXDB_INIT_ORG"),
            "INFLUXDB_INIT_BUCKET": os.getenv("INFLUXDB_INIT_BUCKET"),
        }
        for key, value in env_config.items():
            if value is not None:
                self.config[key] = value

    def get(self, key: str, default: str = "") -> str:
        """Retrieve a configuration value by key, or default value if the key is not found.

        Args:
            key (str): The configuration key.
            default (str): The default value if the key is not found.

        Returns:
            str: The value associated with the key, converted to a string.
        """
        value = self.config.get(key, default)
        return str(value) if value is not None else default
