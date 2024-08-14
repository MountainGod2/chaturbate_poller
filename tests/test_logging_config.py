# ruff: noqa: S101
"""Tests for the logging configuration module."""

import logging

from chaturbate_poller.logging_config import CustomFormatter, SanitizeURLFilter, sanitize_url


def test_sanitize_url() -> None:
    """Test that the sanitize_url function masks sensitive information."""
    url = "https://eventsapi.chaturbate.com/events/username/token/"
    sanitized = sanitize_url(url)
    assert sanitized == "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/"


def test_sanitize_url_filter_with_url_in_message() -> None:
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


def test_sanitize_url_filter_with_plain_message() -> None:
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


def test_sanitize_url_filter_with_args() -> None:
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


def test_sanitize_url_filter_with_none_args() -> None:
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


def test_sanitize_url_filter_with_empty_args_tuple() -> None:
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


def test_sanitize_url_filter_with_mixed_args() -> None:
    """Test that the filter sanitizes URLs and handles non-string args."""
    _filter = SanitizeURLFilter()
    log_record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Message with mixed args",
        args=(
            "https://eventsapi.chaturbate.com/events/username/token/",  # string URL
            123,  # integer
            None,  # NoneType
            "https://example.com/no-token/",  # non-sensitive URL
        ),
        exc_info=None,
    )

    assert _filter.filter(log_record)
    assert log_record.args == (
        "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",  # sanitized
        "123",  # converted to string, not sanitized
        "None",  # converted to string, not sanitized
        "https://example.com/no-token/",  # not sanitized
    )


def test_custom_formatter() -> None:
    """Test the CustomFormatter to ensure it formats log records properly."""
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
