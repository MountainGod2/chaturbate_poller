import logging
import math

import pytest

from chaturbate_poller.logging_config import (
    CustomJSONFormatter,
    SanitizeSensitiveDataFilter,
    sanitize_sensitive_data,
    setup_logging,
)


class TestLoggingConfig:
    """Tests for logging configuration and utilities."""

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
        data_filter = SanitizeSensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="token=abc123",
            args=(),
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.msg == "token=REDACTED"

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="User %s has token %s",
            args=("user123", "events/username/token123"),
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.args == ("user123", "events/USERNAME/TOKEN")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Count: %d URL: %s",
            args=(42, "events/user999/token888"),
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.args == ("42", "events/USERNAME/TOKEN")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg={"url": "events/user123/token456"},
            args=(),
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.msg == {"url": "events/user123/token456"}

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg={"url": "events/user123/token456", "other_field": "normal text"},
            args=(),
            exc_info=None,
        )
        data_filter.filter(record)
        # Dictionary messages should pass through unchanged
        assert record.msg == {"url": "events/user123/token456", "other_field": "normal text"}

    @pytest.mark.parametrize(
        ("input_data", "expected_output"),
        [
            (
                "https://example.com/events/user123/abc123/stream",
                "https://example.com/events/USERNAME/TOKEN/stream",
            ),
            (
                "https://api.example.com/path?token=secret123&other=param",
                "https://api.example.com/path?token=REDACTED&other=param",
            ),
            (math.pi, math.pi),  # Non-string input should be returned as-is
            ("normal text", "normal text"),  # Text without sensitive data
        ],
    )
    def test_sanitize_sensitive_data(
        self, input_data: str | float, expected_output: str | float
    ) -> None:
        """Test that sensitive data is properly sanitized from strings."""
        assert sanitize_sensitive_data(input_data) == expected_output
