# ruff: noqa: S101
"""Tests for the format_messages module."""

import pytest

from chaturbate_poller.format_messages import format_message
from chaturbate_poller.models import Event, EventData


@pytest.mark.asyncio
async def test_format_message_unknown_method() -> None:
    """Test formatting an event with an unknown method."""
    event = Event(method="unknown_method", object=EventData(), id="UNIQUE_EVENT_ID")
    formatted_message = await format_message(event)
    assert formatted_message == "Unknown method: unknown_method"


@pytest.mark.asyncio
async def test_format_message_no_user_or_media() -> None:
    """Test formatting an event with no user or media in the EventData."""
    event_data = EventData(broadcaster="example_broadcaster")
    event = Event(method="mediaPurchase", object=event_data, id="UNIQUE_EVENT_ID")
    formatted_message = await format_message(event)
    assert formatted_message == "Unknown media purchase event"
