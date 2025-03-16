import os
from pathlib import Path
from unittest import mock

from chaturbate_poller.config.manager import ConfigManager


class TestConfigManager:
    """Tests for the configuration manager."""

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_get_with_default(self) -> None:
        """Test retrieving a configuration key with a default value."""
        config_manager = ConfigManager()
        assert config_manager.get("NON_EXISTENT_KEY", "default_value") == "default_value"

    @mock.patch.dict(
        os.environ,
        {
            "CB_USERNAME": "test_user",
            "CB_TOKEN": "test_token",
            "INFLUXDB_URL": "http://localhost:8086",
            "USE_DATABASE": "true",
        },
        clear=True,
    )
    def test_environment_variables(self) -> None:
        """Test loading configuration from environment variables."""
        config_manager = ConfigManager()
        assert config_manager.config["CB_USERNAME"] == "test_user"
        assert config_manager.config["CB_TOKEN"] == "test_token"  # noqa: S105
        assert config_manager.config["INFLUXDB_URL"] == "http://localhost:8086"
        assert config_manager.config["USE_DATABASE"] is True

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("chaturbate_poller.config.manager.dotenv.load_dotenv")
    @mock.patch("chaturbate_poller.config.manager.pathlib.Path.exists", return_value=True)
    def test_env_file_exists(self, mock_exists: mock.Mock, mock_load_dotenv: mock.Mock) -> None:
        """Test loading an environment file when it exists."""
        config_manager = ConfigManager(env_file="test.env")
        mock_exists.assert_called_once_with()
        mock_load_dotenv.assert_called_once_with(dotenv_path=Path("test.env"))
        assert config_manager.config == {"USE_DATABASE": False}

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("chaturbate_poller.config.manager.dotenv.load_dotenv")
    @mock.patch("chaturbate_poller.config.manager.pathlib.Path.exists", return_value=False)
    def test_env_file_not_exists(self, mock_exists: mock.Mock, mock_load_dotenv: mock.Mock) -> None:
        """Test loading an environment file when it does not exist."""
        config_manager = ConfigManager(env_file="test.env")
        mock_exists.assert_called_once_with()
        mock_load_dotenv.assert_not_called()
        assert config_manager.config == {"USE_DATABASE": False}
