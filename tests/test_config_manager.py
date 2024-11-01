import os
from pathlib import Path
from unittest import mock

from chaturbate_poller.config_manager import ConfigManager


class TestConfigManager:
    """Tests for the config module."""

    def test_get_with_default(self) -> None:
        """Test the get method with a default value."""
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
    )
    def test_init_with_env_variables(self) -> None:
        """Test initialization with environment variables."""
        config_manager = ConfigManager()
        assert config_manager.config["CB_USERNAME"] == "test_user"
        assert config_manager.config["CB_TOKEN"] == "test_token"  # noqa: S105
        assert config_manager.config["INFLUXDB_URL"] == "http://localhost:8086"
        assert config_manager.config["USE_DATABASE"] is True

    @mock.patch("chaturbate_poller.config_manager.load_dotenv")
    @mock.patch("chaturbate_poller.config_manager.Path.exists", return_value=True)
    def test_init_with_env_file(self, mock_exists, mock_load_dotenv) -> None:  # noqa: ANN001, ARG002
        """Test initialization with an environment file."""
        config_manager = ConfigManager(env_file="test.env")
        mock_load_dotenv.assert_called_once_with(dotenv_path=Path("test.env"))
        assert config_manager.config == {"USE_DATABASE": False}
