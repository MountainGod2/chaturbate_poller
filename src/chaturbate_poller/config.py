"""Configuration module for the Chaturbate Poller."""

import os
from pathlib import Path

import yaml


def load_config_from_file(config_file: str) -> dict:
    """Load configuration from a file.

    Args:
        config_file (str): The configuration file.

    Returns:
        dict: The configuration.
    """
    with Path(config_file).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_env_variables() -> dict:
    """Load environment variables.

    Returns:
        dict: The environment variables.
    """
    return {
        "username": os.getenv("CB_USERNAME"),
        "token": os.getenv("CB_TOKEN"),
        "use_database": os.getenv("USE_DATABASE", "false").lower() in ["true", "1", "yes"],
    }
