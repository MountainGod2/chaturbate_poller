
from chaturbate_poller.config_manager import ConfigManager


class TestConfigManager:
    """Tests for the config module."""

    def test_get_with_default(self) -> None:
        """Test the get method with a default value."""
        config_manager = ConfigManager()
        assert config_manager.get("NON_EXISTENT_KEY", "default_value") == "default_value"
