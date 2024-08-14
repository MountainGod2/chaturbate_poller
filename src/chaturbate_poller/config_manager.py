"""Centralized configuration module."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration loading from environment variables and configuration files."""

    def __init__(self, config_file: str | None = None, env_file: str = ".env") -> None:
        """Initialize the ConfigManager by loading environment variables or config file.

        Args:
            config_file (str | None): Path to a YAML configuration file. Defaults to None.
            env_file (str): Path to a .env file containing environment variables.
                Defaults to ".env".
        """
        load_dotenv(env_file)
        self.config: dict[str, str | bool | None] = {}

        if config_file and Path(config_file).exists():
            self.load_config_from_file(config_file)

        self.load_env_variables()

    def load_config_from_file(self, config_file: str) -> None:
        """Load configuration from a YAML file and update the config dictionary.

        Args:
            config_file (str): Path to the YAML configuration file.
        """
        with Path(config_file).open(encoding="utf-8") as file:
            file_config = yaml.safe_load(file)
            self.config.update(file_config)

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

    def get(self, key: str, default: str | bool | None = None) -> str:
        """Retrieve a configuration value by key, or default value, if the key is not found.

        Args:
            key (str): The configuration key.
            default (str | bool | None): The default value if the key is not found.
                Defaults to None.

        Returns:
            str: The value associated with the key, or the default value.
        """
        return str(self.config.get(key, default))
