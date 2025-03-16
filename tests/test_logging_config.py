import logging
import math
import sys
from unittest import mock

import pytest

from chaturbate_poller.logging.config import (
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
        formatted = formatter.format(record)
        assert '"message": "test message"' in formatted
        assert '"level": "INFO"' in formatted
        assert '"name": "test"' in formatted
        assert '"time":' in formatted

    def test_custom_json_formatter_with_exception(self) -> None:
        """Test CustomJSONFormatter with exception information."""
        formatter = CustomJSONFormatter()

        def raise_error(message: str) -> None:
            raise ValueError(message)

        try:
            msg = "Test exception"
            raise_error(msg)

        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info(),
            )
            formatted = formatter.format(record)
            assert '"message": "Error occurred"' in formatted
            assert '"level": "ERROR"' in formatted
            assert '"exc_info":' in formatted
            assert "ValueError: Test exception" in formatted

    def test_custom_json_formatter_with_extra_fields(self) -> None:
        """Test CustomJSONFormatter with extra fields."""
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
        record.custom_field = "custom_value"
        formatted = formatter.format(record)
        assert '"custom_field": "custom_value"' in formatted

    def test_setup_logging(self) -> None:
        """Test setup of logging."""
        setup_logging()
        logger = logging.getLogger("chaturbate_poller")
        assert logger.hasHandlers()

    def test_setup_logging_verbose(self) -> None:
        """Test setup of logging in verbose mode."""
        setup_logging(verbose=True)
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

        setup_logging(verbose=False)
        assert logger.level == logging.INFO

    def test_sanitize_filter(self) -> None:
        """Test sanitizing log messages with a filter."""
        data_filter = SanitizeSensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Simple message",
            args=None,
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.msg == "Simple message"
        assert record.args is None

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Numbers: %d %d",
            args=(42, 123),
            exc_info=None,
        )
        data_filter.filter(record)
        assert record.args == ("42", "123")

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
            (math.pi, math.pi),
            ("normal text", "normal text"),
        ],
    )
    def test_sanitize_sensitive_data(
        self, input_data: str | float, expected_output: str | float
    ) -> None:
        """Test that sensitive data is properly sanitized from strings."""
        assert sanitize_sensitive_data(input_data) == expected_output

    def test_sanitize_sensitive_data_edge_cases(self) -> None:
        """Test sanitization with various edge cases."""
        test_cases: list[tuple[str | float, object]] = [
            (None, None),  # type: ignore[list-item]
            ({}, {}),  # type: ignore[list-item]
            (["events/user/token"], ["events/user/token"]),  # type: ignore[list-item]
            (42, "42"),
            (True, "True"),
            (math.pi, str(math.pi)),
            ({"url": "events/user/token"}, {"url": "events/user/token"}),  # type: ignore[list-item]
        ]

        for input_data, expected in test_cases:
            sanitized = sanitize_sensitive_data(input_data)
            if isinstance(input_data, list | dict):
                assert sanitized == expected
            else:
                assert str(sanitized) == str(expected)

    def test_json_logging_non_tty(self) -> None:
        """Test JSON logging configuration in non-TTY mode."""
        setup_logging()
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, CustomJSONFormatter)


@mock.patch("chaturbate_poller.logging.config.rich.traceback.install")
def test_rich_traceback_installation_tty(mock_install: mock.Mock) -> None:
    """Test that rich traceback is installed when stdout is a TTY."""
    with mock.patch("sys.stdout.isatty", return_value=True):
        setup_logging()
        mock_install.assert_called_once()


@mock.patch("chaturbate_poller.logging.config.rich.traceback.install")
def test_rich_traceback_installation_non_tty(mock_install: mock.Mock) -> None:
    """Test that rich traceback is not installed when stdout is not a TTY."""
    with mock.patch("sys.stdout.isatty", return_value=False):
        setup_logging()
        mock_install.assert_not_called()
