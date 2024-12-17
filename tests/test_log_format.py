import logging
from typing import Any

import pytest

from chaturbate_poller.logging_config import (
    SanitizeSensitiveDataFilter,
    sanitize_sensitive_data,
)


@pytest.mark.parametrize(
    ("msg", "expected"),
    [
        (
            "https://eventsapi.chaturbate.com/events/username/token/",
            "https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/",
        ),
        ("This is a log message.", "This is a log message."),
        (
            "User accessed the URL: events/username/token/",
            "User accessed the URL: events/USERNAME/TOKEN/",
        ),
    ],
)
def test_sanitize_url_filter_with_message(msg: str, expected: str) -> None:
    """Test that the filter sanitizes messages appropriately."""
    _filter = SanitizeSensitiveDataFilter()
    log_record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=msg,
        args=(),
        exc_info=None,
    )
    assert _filter.filter(log_record)
    assert log_record.msg == expected


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (
            ("https://eventsapi.chaturbate.com/events/username/token/", 123, "no-url"),
            ("https://eventsapi.chaturbate.com/events/USERNAME/TOKEN/", "123", "no-url"),
        ),
        ((), ()),
        (None, None),
    ],
)
def test_sanitize_url_filter_with_args(args: Any, expected: Any) -> None:
    """Test that the filter sanitizes arguments appropriately."""
    _filter = SanitizeSensitiveDataFilter()
    log_record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Message with args",
        args=args,
        exc_info=None,
    )
    assert _filter.filter(log_record)
    assert log_record.args == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("events/user123/token456", "events/USERNAME/TOKEN"),
        ("no_sensitive_info_here", "no_sensitive_info_here"),
        (123, 123),
        (123.456, 123.456),
    ],
)
def test_sanitize_sensitive_data(url: str, expected: str) -> None:
    """Test the sanitize_sensitive_data function."""
    assert sanitize_sensitive_data(url) == expected


def test_sanitize_url_filter_with_mixed_args() -> None:
    """Test that the filter sanitizes mixed types of arguments."""
    _filter = SanitizeSensitiveDataFilter()
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
