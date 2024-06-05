"""Tests for `event_handler.py`."""

import re
from typing import Any

import pytest

from chaturbate_event_listener.event_handler import EventHandler
from chaturbate_event_listener.logger import logger


@pytest.fixture()
def event_handler() -> EventHandler:
    """Return an instance of EventHandler."""
    return EventHandler()


@pytest.mark.parametrize(
    ("method", "message", "expected"),
    [
        (
            "broadcastStart",
            {"object": {"broadcaster": {"username": "test_broadcaster"}}},
            "Broadcast started by test_broadcaster",
        ),
        (
            "broadcastStart",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "broadcastStop",
            {"object": {"broadcaster": {"username": "test_broadcaster"}}},
            "Broadcast stopped by test_broadcaster",
        ),
        (
            "broadcastStop",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "userEnter",
            {"object": {"user": {"username": "test_user"}}},
            "test_user entered the room",
        ),
        (
            "userEnter",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "userLeave",
            {"object": {"user": {"username": "test_user"}}},
            "test_user left the room",
        ),
        (
            "userLeave",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "follow",
            {"object": {"user": {"username": "test_user"}}},
            "test_user has followed",
        ),
        (
            "follow",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "unfollow",
            {"object": {"user": {"username": "test_user"}}},
            "test_user has unfollowed",
        ),
        (
            "unfollow",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "fanclubJoin",
            {"object": {"user": {"username": "test_user"}}},
            "test_user joined the fan club",
        ),
        (
            "fanclubJoin",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "chatMessage",
            {
                "object": {
                    "user": {"username": "test_user"},
                    "message": {"message": "test_message"},
                }
            },
            "test_user sent chat message: test_message",
        ),
        (
            "chatMessage",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "privateMessage",
            {
                "object": {
                    "message": {
                        "message": "test_message",
                        "toUser": "test_to_user",
                        "fromUser": "test_from_user",
                    }
                }
            },
            "test_from_user sent private message to test_to_user: test_message",
        ),
        (
            "privateMessage",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "tip",
            {
                "object": {
                    "user": {"username": "test_user"},
                    "tip": {
                        "tokens": 100,
                        "message": " | test_message",
                        "isAnon": True,
                    },
                }
            },
            "test_user tipped 100 tokens anonymously with message: test_message",
        ),
        (
            "tip",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "roomSubjectChange",
            {"object": {"subject": "test_subject"}},
            "Room subject changed to: test_subject",
        ),
        (
            "roomSubjectChange",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
        (
            "mediaPurchase",
            {
                "object": {
                    "user": {"username": "test_user"},
                    "media": {"type": "photos", "name": "test_media"},
                }
            },
            "test_user purchased photos set: test_media",
        ),
        (
            "mediaPurchase",
            {"object": {}},
            "Incomplete EventHandler event received: {'object': {}}",
        ),
    ],
)
def test_event_handler_methods(
    event_handler: EventHandler,
    method: str,
    message: dict[str, Any],
    expected: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test event_handler methods."""
    with caplog.at_level(logger.level):
        function = re.sub(r"(?<!^)(?=[A-Z])", "_", method).lower()
        getattr(event_handler, f"handle_{function}")(message)

        assert expected in caplog.text
        if "Incomplete EventHandler" in expected:
            assert caplog.records[-1].levelname == "WARNING"
        else:
            assert caplog.records[-1].levelname == "INFO"


@pytest.mark.parametrize(
    ("data", "log_message"),
    [
        (
            {
                "method": "chatMessage",
                "object": {
                    "user": {"username": "test_user"},
                    "message": {"message": "test_message"},
                },
            },
            "test_user sent chat message: test_message",
        ),
        (
            {
                "method": "unknownMethod",
                "object": {
                    "user": {"username": "test_user"},
                },
            },
            "Unknown method: unknownMethod",
        ),
    ],
)
def test_default_event_callback(
    event_handler: EventHandler,
    caplog: pytest.LogCaptureFixture,
    data: dict[str, Any],
    log_message: str,
) -> None:
    """Test default_event_callback."""
    with caplog.at_level(logger.level):
        event_handler.default_event_callback(data)

        assert log_message in caplog.text
        if "Unknown method" in log_message:
            assert caplog.records[-1].levelname == "WARNING"
        else:
            assert caplog.records[-1].levelname == "INFO"

    with caplog.at_level(logger.level):
        data["method"] = None
        event_handler.default_event_callback(data)

        assert "Unknown method" in caplog.text
        assert caplog.records[-1].levelname == "WARNING"


def test_event_handler_call(
    event_handler: EventHandler, caplog: pytest.LogCaptureFixture
) -> None:
    """Test event_handler call."""
    data = {
        "method": "chatMessage",
        "object": {
            "user": {"username": "test_user"},
            "message": {"message": "test_message"},
        },
    }
    event_handler(data)

    assert "test_user sent chat message: test_message" in caplog.text
