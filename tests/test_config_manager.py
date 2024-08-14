# ruff: noqa: S101
"""Tests for the config module."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from chaturbate_poller.config_manager import ConfigManager


def test_load_config_from_file() -> None:
    """Test loading configuration from a YAML file."""
    with patch("os.getenv", side_effect=lambda k, d=None: d):  # noqa: ARG005, SIM117
        with TemporaryDirectory() as tempdir:
            config_path = Path(tempdir) / "config.yaml"
            config_path.write_text(
                """
            CB_USERNAME: "file_user"
            CB_TOKEN: "file_token"
            """,
                encoding="utf-8",
            )

            config_manager = ConfigManager(config_file=str(config_path))
            assert config_manager.get("CB_USERNAME") == "file_user"
            assert config_manager.get("CB_TOKEN") == "file_token"


def test_load_env_and_file_combined() -> None:
    """Test loading configuration from both environment variables and a file."""
    with patch("os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d):  # noqa: SIM117
        with TemporaryDirectory() as tempdir:
            config_path = Path(tempdir) / "config.yaml"
            config_path.write_text(
                """
            CB_TOKEN: "file_token"
            """,
                encoding="utf-8",
            )

            config_manager = ConfigManager(config_file=str(config_path))
            assert config_manager.get("CB_USERNAME") == "env_user"
            assert config_manager.get("CB_TOKEN") == "file_token"


def test_env_overrides_file() -> None:
    """Test that environment variables override the values in the configuration file."""
    with patch("os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d):  # noqa: SIM117
        with TemporaryDirectory() as tempdir:
            config_path = Path(tempdir) / "config.yaml"
            config_path.write_text(
                """
            CB_USERNAME: "file_user"
            CB_TOKEN: "file_token"
            """,
                encoding="utf-8",
            )

            config_manager = ConfigManager(config_file=str(config_path))
            assert config_manager.get("CB_USERNAME") == "env_user"
            assert config_manager.get("CB_TOKEN") == "file_token"  # From the file


def test_get_with_default() -> None:
    """Test the get method with a default value."""
    config_manager = ConfigManager()
    assert config_manager.get("NON_EXISTENT_KEY", "default_value") == "default_value"
