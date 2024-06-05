"""Tests for the client module."""

import pytest
from aiohttp import ClientResponseError, ClientSession, RequestInfo
from aioresponses import aioresponses
from dotenv import load_dotenv
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from chaturbate_event_listener.client import ChaturbateEventClient
from chaturbate_event_listener.errors import (
    ChaturbateEventListenerError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

load_dotenv()


@pytest.fixture()
def event_client() -> ChaturbateEventClient:
    """Return a ChaturbateEventClient instance."""
    test_api_url = "https://mocki.io/v1/f334537a-dffb-47e2-a4f0-998d935eb86b"
    return ChaturbateEventClient(url=test_api_url)


@pytest.mark.asyncio()
async def test_aenter(event_client: ChaturbateEventClient) -> None:
    """Test the __aenter__ method."""
    async with event_client:
        assert isinstance(event_client.session, ClientSession)


@pytest.mark.asyncio()
async def test_aexit(event_client: ChaturbateEventClient) -> None:
    """Test the __aexit__ method."""
    async with event_client:
        pass
    assert event_client.session is None


@pytest.mark.asyncio()
async def test_retrieve_events_no_session(event_client: ChaturbateEventClient) -> None:
    """Test the retrieve_events method with no session."""
    with pytest.raises(RuntimeError, match="Client session is not initialized"):
        await event_client.retrieve_events("http://test.com")


@pytest.mark.asyncio()
async def test_retrieve_events_unexpected_status(
    event_client: ChaturbateEventClient,
) -> None:
    """Test the retrieve_events method with an unexpected status code."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout=1"
            mocked.get(url, status=418)

            with pytest.raises(ClientResponseError):
                assert await event_client.retrieve_events(url) is None


@pytest.mark.asyncio()
async def test_retrieve_events(event_client: ChaturbateEventClient) -> None:
    """Test the retrieve_events method."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout=1"
            mocked.get(url, payload={"events": [], "nextUrl": None})

            assert await event_client.retrieve_events(url) == {
                "events": [],
                "nextUrl": None,
            }


@pytest.mark.asyncio()
async def test_retrieve_events_timeout_error(
    event_client: ChaturbateEventClient,
) -> None:
    """Test the retrieve_events method with a timeout error."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout=1"
            mocked.get(url, exception=TimeoutError)

            with pytest.raises(ChaturbateEventListenerError):
                assert await event_client.retrieve_events(url) is None


@pytest.mark.asyncio()
async def test_process_events_no_events(event_client: ChaturbateEventClient) -> None:
    """Test the process_events method with no events."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout={event_client.timeout}"
            mocked.get(url, payload={"events": [], "nextUrl": None})

            await event_client.process_events(url)


@pytest.mark.asyncio()
async def test_process_events_calls_event_handler(
    event_client: ChaturbateEventClient,
) -> None:
    """Test the process_events method calls the event_handler."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout={event_client.timeout}"
            mocked.get(
                url,
                payload={
                    "events": [
                        {"type": "test", "data": "test"},
                    ],
                    "nextUrl": None,
                },
            )

            def event_handler(message: dict[str, str]) -> None:
                assert message == {"type": "test", "data": "test"}

            event_client.event_handler = event_handler
            await event_client.process_events(url)


@pytest.mark.asyncio()
async def test_process_events_no_url(event_client: ChaturbateEventClient) -> None:
    """Test the process_events method with no URL."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout={event_client.timeout}"
            mocked.get(url, payload={"events": [], "nextUrl": None})

            await event_client.process_events()


@pytest.mark.asyncio()
async def test_process_events_next_url() -> None:
    """Test the process_events method with a next URL."""
    async with ChaturbateEventClient(
        is_testbed=True,
    ) as event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout={event_client.timeout}"
            next_url = f"{event_client.base_url}?timeout={event_client.timeout}"
            mocked.get(
                url,
                payload={
                    "events": [],
                    "nextUrl": next_url,
                },
            )
            mocked.get(
                next_url,
                payload={"events": [], "nextUrl": None},
            )

            await event_client.process_events(url)


@pytest.mark.parametrize(
    ("status", "message", "expected"),
    [
        (401, "Unauthorized access", UnauthorizedError),
        (403, "Forbidden access", ForbiddenError),
        (404, "Resource not found", NotFoundError),
    ],
)
@pytest.mark.asyncio()
async def test_process_events_error(
    event_client: ChaturbateEventClient,
    status: int,
    message: str,
    expected: type[Exception] | tuple[type[Exception], ...],
) -> None:
    """Test the process_events method with an error status."""
    async with event_client:
        with aioresponses() as mocked:
            url = f"{event_client.base_url}?timeout={event_client.timeout}"
            mocked.get(url, status=status)

            with pytest.raises(expected, match=message):
                await event_client.process_events(url)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, True),
        (403, True),
        (404, True),
        (500, False),
        (599, False),
        (600, True),
    ],
)
@pytest.mark.asyncio()
async def test_is_fatal_error(
    status: int, *, expected: bool, event_client: ChaturbateEventClient
) -> None:
    """Test the is_fatal_error function."""
    exception = ClientResponseError(
        RequestInfo(
            method="GET",
            url=URL("http://test.com"),
            headers=CIMultiDictProxy(CIMultiDict()),
        ),
        history=(),
        status=status,
        message="",
    )
    assert event_client.is_fatal_error(exception) == expected
