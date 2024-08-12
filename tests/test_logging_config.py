# ruff: noqa: S101
"""Tests for the logging configuration module."""

import logging

from chaturbate_poller.logging_config import CustomFormatter, SanitizeURLFilter, sanitize_url


def test_sanitize_url() -> None:
    """Test that the sanitize_url function masks sensitive information."""
    url = "https://eventsapi.chaturbate.com/events/username/token/"
    sanitized = sanitize_url(url)
    assert sanitized == "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/"


def test_sanitize_url_filter() -> None:
    """Test the SanitizeURLFilter to ensure it sanitizes log messages."""
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
