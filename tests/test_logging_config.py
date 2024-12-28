import logging

from chaturbate_poller.logging_config import (
    CustomJSONFormatter,
    SanitizeSensitiveDataFilter,
    sanitize_sensitive_data,
    setup_logging,
)


class TestLoggingConfig:
    """Tests for logging configuration and utilities."""

    def test_sanitize_sensitive_data(self) -> None:
        """Test sanitizing sensitive data in log messages."""
        assert sanitize_sensitive_data("events/user123/token456") == "events/USERNAME/TOKEN"
        assert sanitize_sensitive_data("token=abc123") == "token=REDACTED"

    def test_custom_json_formatter(self) -> None:
        """Test CustomJSONFormatter."""
        formatter = CustomJSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="test message",
            args=(),
            exc_info=None,
        )
        json_record = formatter.json_record("test message", {}, record)
        assert json_record["message"] == "test message"
        assert json_record["level"] == "INFO"

    def test_setup_logging(self) -> None:
        """Test setup of logging."""
        setup_logging()
        logger = logging.getLogger("chaturbate_poller")
        assert logger.hasHandlers()

    def test_sanitize_filter(self) -> None:
        """Test sanitizing log messages with a filter."""
        _filter = SanitizeSensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="token=abc123",
            args=(),
            exc_info=None,
        )
        _filter.filter(record)
        assert record.msg == "token=REDACTED"
