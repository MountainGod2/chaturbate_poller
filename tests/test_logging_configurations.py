import logging
import uuid
from logging import LogRecord
from pathlib import Path

from chaturbate_poller.logging_config import (
    LOGGING_CONFIG,
    AddCorrelationIDFilter,
    CustomFormatter,
    CustomJSONFormatter,
    SanitizeSensitiveDataFilter,
    sanitize_sensitive_data,
    setup_logging,
    log_filename
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

    def test_add_correlation_id_filter(self) -> None:
        """Test add correlation ID filter."""
        filter = AddCorrelationIDFilter()  # noqa: A001
        record = LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        filter.filter(record)
        assert hasattr(record, "correlation_id")
        assert isinstance(record.correlation_id, uuid.UUID)

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
        record.correlation_id = uuid.uuid4()
        json_record = formatter.json_record("test message", {}, record)
        assert json_record["message"] == "test message"
        assert json_record["level"] == "INFO"
        assert json_record["name"] == "test"
        assert "correlation_id" in json_record

    def test_setup_logging(self) -> None:
        """Test setup logging."""
        setup_logging()
        logger = logging.getLogger("chaturbate_poller")
        assert logger.hasHandlers() is True

    def test_setup_create_directory(self) -> None:
        """Test setup create directory."""
        setup_logging()

        log_file = Path(log_filename)
        assert log_file.exists() is True
