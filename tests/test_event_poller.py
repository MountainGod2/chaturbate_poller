# ruff: noqa
"""Tests for the EventPoller class."""

from unittest.mock import AsyncMock, patch

import pytest

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.event_poller import EventPoller
from chaturbate_event_listener.models import Event, EventObject


@pytest.fixture()
def config():
    return Config(username="testuser", token="testtoken")


@pytest.fixture()
def event_poller(config):
    return EventPoller(config)


@pytest.mark.asyncio()
async def test_poll(event_poller) -> None:
    with patch.object(event_poller, "get_events", new_callable=AsyncMock) as mock_get_events:
        mock_get_events.return_value = ([], None)
        await event_poller.poll()
        mock_get_events.assert_called_once_with(event_poller.session_factory(), event_poller.url)


@pytest.mark.asyncio()
async def test_handle_event(event_poller) -> None:
    mock_event = Event(method="tip", id="1", object=EventObject(broadcaster="test"))
    mock_callback = AsyncMock()
    event_poller.register_callback("tip", mock_callback)
    event_poller._handle_event(mock_event)
    mock_callback.assert_called_once_with(mock_event)


@pytest.mark.asyncio()
async def test_get_events(event_poller) -> None:
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"events": [], "nextUrl": None}
    mock_session.get.return_value = mock_response
    events, next_url = await event_poller.get_events(mock_session, "http://test.com")
    assert events == []
    assert next_url is None
