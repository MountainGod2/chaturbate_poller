import logging

from chaturbate_poller.logging_config import (
    CustomFormatter,
    SanitizeURLFilter,
    sanitize_url,
)


class TestLogFormat:
    """Tests for the log format."""

    def test_format_log(self) -> None:
        """Test log format."""
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=None,
            exc_info=None,
        )
        formatter = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        formatted = formatter.format(log_record)
        assert "Test message" in formatted

    def test_sanitize_url_filter_with_url_in_message(self) -> None:
        """Test that the filter sanitizes a URL in the message."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="https://eventsapi.chaturbate.com/events/username/token/",
            args=(),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/"

    def test_sanitize_url_filter_with_plain_message(self) -> None:
        """Test that the filter does not modify a message without a URL."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="This is a log message.",
            args=(),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "This is a log message."

    def test_sanitize_url_filter_with_args(self) -> None:
        """Test that the filter sanitizes URLs in the arguments."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with args",
            args=("https://eventsapi.chaturbate.com/events/username/token/", 123, "no-url"),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.args == (
            "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",
            "123",
            "no-url",
        )

    def test_sanitize_url_filter_with_none_args(self) -> None:
        """Test that the filter works when args is None."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="This is a log message with no args.",
            args=None,
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "This is a log message with no args."
        assert log_record.args is None

    def test_sanitize_url_filter_with_empty_args_tuple(self) -> None:
        """Test that the filter handles an empty args tuple."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with empty args tuple",
            args=(),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "Message with empty args tuple"
        assert log_record.args == ()

    def test_sanitize_url_filter_with_mixed_args(self) -> None:
        """Test that the filter sanitizes URLs and handles non-string args."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message with mixed args",
            args=(
                "https://eventsapi.chaturbate.com/events/username/token/",
                123,
                None,
                "https://example.com/no-token/",
            ),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.args == (
            "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",
            "123",
            "None",
            "https://example.com/no-token/",
        )

    def test_sanitize_url_filter_with_string_message(self) -> None:
        """Test that the filter sanitizes a string message."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User accessed the URL: events/username/token/",
            args=(),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "User accessed the URL: events/USERNAME/TOKEN/"

    def test_sanitize_url_filter_with_args_string(self) -> None:
        """Test that the filter sanitizes a URL in args when message is not a URL."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Accessing events",
            args=("events/username/token/",),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "Accessing events"
        assert log_record.args == ("events/USERNAME/TOKEN/",)

    def test_sanitize_url_filter_with_multiple_args(self) -> None:
        """Test that the filter sanitizes URLs in multiple args."""
        _filter = SanitizeURLFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User actions",
            args=(
                "events/username/token/",
                "other_arg",
                "another/events/username/token/",
            ),
            exc_info=None,
        )
        assert _filter.filter(log_record)
        assert log_record.msg == "User actions"
        assert log_record.args == (
            "events/USERNAME/TOKEN/",
            "other_arg",
            "another/events/USERNAME/TOKEN/",
        )

    def test_sanitize_url(self) -> None:
        """Test the sanitize_url function."""
        assert sanitize_url("events/user123/token456") == "events/USERNAME/TOKEN"
        assert sanitize_url("no_sensitive_info_here") == "no_sensitive_info_here"
        assert sanitize_url(123) == 123
        assert sanitize_url(123.456) == 123.456

    def test_sanitize_url_filter(self) -> None:
        """Test the SanitizeURLFilter class."""
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_path",
            lineno=10,
            msg="events/user123/token456",
            args=(),
            exc_info=None,
        )
        filter = SanitizeURLFilter()  # noqa: A001
        filter.filter(log_record)
        assert log_record.msg == "events/USERNAME/TOKEN"

        log_record.args = ("events/user123/token456", 123, "no_sensitive_info_here")
        filter.filter(log_record)
        assert log_record.args == ("events/USERNAME/TOKEN", "123", "no_sensitive_info_here")

    def test_custom_formatter(self) -> None:
        """Test custom log formatter."""
        formatter = CustomFormatter("%(module)s - %(message)s")
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_path",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        log_record.module = "chaturbate_poller.logging_config"
        formatted_message = formatter.format(log_record)
        assert formatted_message == "logging_config - Test message"

    def test_filter_sanitizes_url(self, log_record: logging.LogRecord) -> None:
        """Test that the filter sanitizes URLs in the log message."""
        filter = SanitizeURLFilter()  # noqa: A001
        filter.filter(log_record)
        assert log_record.msg == "events/USERNAME/TOKEN"

    def test_filter_sanitizes_url_in_args(self, log_record_with_args: logging.LogRecord) -> None:
        """Test that the filter sanitizes URLs in the log arguments."""
        filter = SanitizeURLFilter()  # noqa: A001
        filter.filter(log_record_with_args)
        assert log_record_with_args.args == ("events/USERNAME/TOKEN", "42")

    def test_filter_does_not_modify_non_string_args(self) -> None:
        """Test that the filter does not modify non-string arguments."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="User accessed the URL",
            args=(42, 3.14),
            exc_info=None,
        )
        filter = SanitizeURLFilter()  # noqa: A001
        filter.filter(record)
        assert record.args == ("42", "3.14")
