from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from chaturbate_poller.config_manager import ConfigManager


class TestConfigManager:
    """Tests for the config module."""

    def test_load_config_from_file(self, mocker: Any) -> None:
        """Test loading configuration from a YAML file."""
        mocker.patch("os.getenv", side_effect=lambda _, d=None: d)
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

    def test_load_env_and_file_combined(self, mocker: Any) -> None:
        """Test loading configuration from both environment variables and a file."""
        mocker.patch(
            "os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d
        )
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

    def test_env_overrides_file(self, mocker: Any) -> None:
        """Test that environment variables override the values in the configuration file."""
        mocker.patch(
            "os.getenv", side_effect=lambda k, d=None: "env_user" if k == "CB_USERNAME" else d
        )
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
            assert config_manager.get("CB_TOKEN") == "file_token"

    def test_get_with_default(self) -> None:
        """Test the get method with a default value."""
        config_manager = ConfigManager()
        assert config_manager.get("NON_EXISTENT_KEY", "default_value") == "default_value"
