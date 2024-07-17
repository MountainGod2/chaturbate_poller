"""Tests for the EventPoller class."""

import asyncio
from typing import Never
from unittest import mock

import pytest
from aioresponses import aioresponses
from tenacity import RetryError

from chaturbate_event_listener.config import Config
from chaturbate_event_listener.errors import UnauthorizedError
from chaturbate_event_listener.event_poller import EventPoller
from chaturbate_event_listener.models import Event

# Sample data for testing
sample_event = {
    "method": "tip",
    "id": "event_id",
    "object": {
        "broadcaster": "broadcaster_name",
        "tip": {"isAnon": False, "message": "Sample message", "tokens": 100},
        "user": {
            "username": "test_user",
            "inFanclub": False,
            "hasTokens": True,
            "isMod": False,
            "recentTips": "None",
            "gender": "M",
            "subgender": "None",
            "colorGroup": None,
            "fcAutoRenew": None,
            "hasDarkmode": None,
            "inPrivateShow": None,
            "isBroadcasting": None,
            "isFollower": None,
            "isOwner": None,
            "isSilenced": None,
            "isSpying": None,
            "language": None,
        },
    },
}


@pytest.fixture()
def config() -> Config:
    """Return a Config object with test values."""
    return Config(username="testuser", token="testtoken")  # noqa: S106


@pytest.fixture()
def poller(config: Config) -> EventPoller:
    """Return an EventPoller object with test values."""
    return EventPoller(config)


@pytest.mark.asyncio()
async def test_get_events_success(poller: EventPoller) -> None:
    """Test the get_events method with a successful response."""
    with aioresponses() as m:
        url = poller.url
        m.get(url, payload={"events": [sample_event], "nextUrl": None})

        async with poller.get_client_session() as session:
            events, next_url = await poller.get_events(session, url)

        assert len(events) == 1
        assert events[0].method == "tip"
        assert events[0].id == "event_id"
        assert next_url is None


@pytest.mark.asyncio()
async def test_get_events_server_error(poller: EventPoller) -> None:
    """Test the get_events method with a server error."""
    with aioresponses() as m:
        url = poller.url
        m.get(url, status=500, repeat=True)
        poller.get_events.retry.sleep = mock.AsyncMock()
        async with poller.get_client_session() as session:
            with pytest.raises(RetryError):
                await poller.get_events(session, url)


@pytest.mark.asyncio()
async def test_get_events_unauthorized_error(poller: EventPoller) -> None:
    """Test the get_events method with an unauthorized error."""
    with aioresponses() as m:
        url = poller.url
        m.get(url, status=401)

        async with poller.get_client_session() as session:
            with pytest.raises(UnauthorizedError):
                await poller.get_events(session, url)


@pytest.mark.asyncio()
async def test_format_tip_message(poller: EventPoller) -> None:
    """Test the _format_tip_message method."""
    event = Event.from_dict(sample_event)
    message = poller._format_tip_message(event)  # noqa: SLF001
    expected_message = "User test_user tipped 100 tokens with message: 'Sample message'"
    assert message == expected_message


@pytest.mark.asyncio()
async def test_get_events_empty_response(poller: EventPoller) -> None:
    """Test the get_events method with an empty response."""
    with aioresponses() as m:
        url = poller.url
        m.get(url, payload={"events": [], "nextUrl": None})

        async with poller.get_client_session() as session:
            events, next_url = await poller.get_events(session, url)

        assert len(events) == 0
        assert next_url is None


@pytest.mark.asyncio()
async def test_get_events_with_next_url(poller: EventPoller) -> None:
    """Test the get_events method with a next URL."""
    with aioresponses() as m:
        url = poller.url
        next_url = "http://example.com/next"
        m.get(url, payload={"events": [sample_event], "nextUrl": next_url})

        async with poller.get_client_session() as session:
            events, fetched_next_url = await poller.get_events(session, url)

        assert len(events) == 1
        assert events[0].method == "tip"
        assert events[0].id == "event_id"
        assert fetched_next_url == next_url


@pytest.mark.asyncio()
async def test_event_parsing_failure(poller: EventPoller) -> None:
    """Test the get_events method with an invalid event."""
    with aioresponses() as m:
        url = poller.url
        invalid_event = {"invalid_key": "invalid_value"}
        m.get(url, payload={"events": [invalid_event], "nextUrl": None})

        async with poller.get_client_session() as session:
            events, next_url = await poller.get_events(session, url)

        assert len(events) == 0
        assert next_url is None


@pytest.mark.asyncio()
async def test_register_callback_and_handle_event(poller: EventPoller) -> None:
    """Test the register_callback and _handle_event methods."""
    callback_called = False

    def mock_callback(event: Event) -> None:  # noqa: ARG001
        nonlocal callback_called
        callback_called = True

    poller.register_callback("tip", mock_callback)
    event = Event.from_dict(sample_event)
    poller._handle_event(event)  # noqa: SLF001

    assert callback_called


@pytest.mark.asyncio()
async def test_shutdown(poller: EventPoller) -> None:
    """Test the shutdown method."""

    async def mock_poll() -> Never:
        await asyncio.sleep(1)  # simulate some work
        raise asyncio.CancelledError

    poller.poll = mock_poll

    # Ensure that shutdown is called and raises CancelledError
    with pytest.raises(asyncio.CancelledError):
        await poller.shutdown(asyncio.get_event_loop())
