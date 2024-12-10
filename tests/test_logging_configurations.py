import logging
from logging import LogRecord
from pathlib import Path
from unittest.mock import patch

import pytest

from chaturbate_poller.logging_config import (
    LOGGING_CONFIG,
    CustomFormatter,
    CustomJSONFormatter,
    SanitizeSensitiveDataFilter,
    log_filename,
    sanitize_sensitive_data,
    setup_logging,
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

    def test_setup_create_directory(self) -> None:
        """Test setup create directory."""
        setup_logging()

        log_file = Path(log_filename)
        assert log_file.exists() is True

    def test_setup_logging_creates_log_directory(self) -> None:
        """Test setup_logging creates the log directory if it does not exist."""
        with (
            patch(
                "chaturbate_poller.logging_config.Path.exists", return_value=False
            ) as mock_exists,
            patch("chaturbate_poller.logging_config.Path.mkdir") as mock_mkdir,
        ):
            setup_logging()
            mock_exists.assert_called_once()  # Verify exists() is called to check for directory
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_setup_logging_with_existing_directory(self) -> None:
        """Test setup_logging does not create the log directory if it exists."""
        with (
            patch("chaturbate_poller.logging_config.Path.exists", return_value=True) as mock_exists,
            patch("chaturbate_poller.logging_config.Path.mkdir") as mock_mkdir,
        ):
            setup_logging()
            mock_exists.assert_called_once()
            mock_mkdir.assert_not_called()

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

    def test_setup_logging_permission_error(self) -> None:
        """Test setup_logging handles PermissionError correctly."""
        error_msg = "Permission denied"
        permission_error = PermissionError(error_msg)

        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.mkdir", side_effect=permission_error),
            patch("logging.critical") as mock_critical,
        ):
            with pytest.raises(RuntimeError) as exc_info:
                setup_logging()

            expected_msg = "Cannot create or access log directory 'logs': Permission denied"
            assert str(exc_info.value) == expected_msg
            assert exc_info.value.__cause__ == permission_error

            mock_critical.assert_called_once_with(
                "Cannot create or access log directory '%s': %s", Path("logs"), permission_error
            )
