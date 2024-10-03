import logging

from chaturbate_poller.logging_config import (
    LOGGING_CONFIG,
    CustomFormatter,
)


class TestLoggingConfigurations:
    """Tests for logging configurations."""

    def test_module_logging_configuration(self) -> None:
        """Test module logging configuration."""
        assert isinstance(LOGGING_CONFIG, dict)
        assert LOGGING_CONFIG.get("version") == 1
        assert LOGGING_CONFIG.get("disable_existing_loggers") is False

    def test_detailed_formatter(self) -> None:
        """Test detailed formatter."""
        formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        formatted = formatter.format(log_record)
        assert "Test message" in formatted
