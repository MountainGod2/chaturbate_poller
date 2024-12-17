import logging
from logging import LogRecord

import pytest

from chaturbate_poller.logging_config import (
    LOGGING_CONFIG,
    CustomJSONFormatter,
    SanitizeSensitiveDataFilter,
    sanitize_sensitive_data,
    setup_logging,
)


@pytest.fixture
def log_record() -> LogRecord:
    """Fixture to create a log record."""
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None,
    )


class TestLoggingConfigurations:
    """Tests for logging configurations."""

    def test_module_logging_configuration(self) -> None:
        """Test module logging configuration."""
        assert isinstance(LOGGING_CONFIG, dict)
        assert LOGGING_CONFIG.get("version") == 1
        assert LOGGING_CONFIG.get("disable_existing_loggers") is False

    def test_sanitize_sensitive_data(self) -> None:
        """Test sanitize sensitive data."""
        assert sanitize_sensitive_data("events/user123/token123") == "events/USERNAME/TOKEN"
        assert sanitize_sensitive_data("token=abc123") == "token=REDACTED"
        assert sanitize_sensitive_data("no_sensitive_data_here") == "no_sensitive_data_here"
        assert sanitize_sensitive_data(123.45) == 123.45

    def test_sanitize_sensitive_data_filter(self) -> None:
        """Test sanitize sensitive data filter."""
        filter = SanitizeSensitiveDataFilter()  # noqa: A001
        record = LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="events/user123/token123",
            args=(),
            exc_info=None,
        )
        filter.filter(record)
        assert record.msg == "events/USERNAME/TOKEN"

        record = LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="token=abc123",
            args=(),
            exc_info=None,
        )
        filter.filter(record)
        assert record.msg == "token=REDACTED"

    def test_custom_json_formatter(self) -> None:
        """Test custom JSON formatter."""
        formatter = CustomJSONFormatter()
        record = LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        json_record = formatter.json_record("test message", {}, record)
        assert json_record["message"] == "test message"
        assert json_record["level"] == "INFO"
        assert json_record["name"] == "test"
        assert "time" in json_record

    def test_setup_logging(self) -> None:
        """Test setup logging."""
        setup_logging()
        logger = logging.getLogger("chaturbate_poller")
        assert logger.hasHandlers() is True

    def test_sanitize_sensitive_data_no_filter_on_non_str(self) -> None:
        """Test that sanitize_sensitive_data does not alter non-string log messages."""
        filter = SanitizeSensitiveDataFilter()  # noqa: A001
        record = LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=12345,
            args=(),
            exc_info=None,
        )
        assert filter.filter(record)
        assert record.msg == 12345

    def test_verbose_log_level(self) -> None:
        """Test that the logger level is set to DEBUG when verbose flag is set."""
        setup_logging(verbose=True)
        assert logging.getLogger("chaturbate_poller").getEffectiveLevel() == logging.DEBUG
