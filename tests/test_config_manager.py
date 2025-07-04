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

        # All environment variables should be loaded with default values
        expected_config = {
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
        assert config_manager.config == expected_config

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("chaturbate_poller.config.manager.dotenv.load_dotenv")
    @mock.patch("chaturbate_poller.config.manager.pathlib.Path.exists", return_value=False)
    def test_env_file_not_exists(self, mock_exists: mock.Mock, mock_load_dotenv: mock.Mock) -> None:
        """Test loading an environment file when it does not exist."""
        config_manager = ConfigManager(env_file="test.env")
        mock_exists.assert_called_once_with()
        mock_load_dotenv.assert_not_called()

        # All environment variables should be loaded with default values
        expected_config = {
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
        assert config_manager.config == expected_config

    def test_str_to_bool(self) -> None:
        """Test string to boolean conversion."""
        config_manager = ConfigManager()

        # Test true values
        assert config_manager.str_to_bool("true") is True
        assert config_manager.str_to_bool("True") is True
        assert config_manager.str_to_bool("TRUE") is True
        assert config_manager.str_to_bool("1") is True
        assert config_manager.str_to_bool("yes") is True
        assert config_manager.str_to_bool("Yes") is True
        assert config_manager.str_to_bool("YES") is True

        # Test false values
        assert config_manager.str_to_bool("false") is False
        assert config_manager.str_to_bool("False") is False
        assert config_manager.str_to_bool("FALSE") is False
        assert config_manager.str_to_bool("0") is False
        assert config_manager.str_to_bool("no") is False
        assert config_manager.str_to_bool("anything_else") is False

    @mock.patch.dict(
        os.environ,
        {
            "CB_USERNAME": "test_user",
            "USE_DATABASE": "true",
        },
        clear=True,
    )
    def test_get_bool_method(self) -> None:
        """Test the get_bool method with different value types."""
        config_manager = ConfigManager()

        # Test boolean environment variable
        assert config_manager.get_bool("USE_DATABASE") is True

        # Test string that should be converted to boolean
        assert config_manager.get_bool("USE_DATABASE") is True

        # Test non-existent key with default
        assert config_manager.get_bool("NON_EXISTENT_KEY", default=True) is True
        assert config_manager.get_bool("NON_EXISTENT_KEY", default=False) is False

        # Test string value that's not boolean-ish
        assert config_manager.get_bool("CB_USERNAME", default=False) is False
