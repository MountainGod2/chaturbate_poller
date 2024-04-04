"""Tests for the chaturbate_poller module."""

from json import JSONDecodeError
from unittest.mock import MagicMock

import pytest
from chaturbate_poller.chaturbate_poller import ChaturbateClient, need_retry
from chaturbate_poller.models import EventsAPIResponse
from httpx import (
    AsyncClient,
    HTTPStatusError,
    Request,
    RequestError,
    Response,
    TimeoutException,
)

USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = "https://events.testbed.cb.dev/events/testuser/testtoken/"


# Mock the HTTP client at module level for better performance
@pytest.fixture()
def http_client_mock(
    mocker,  # noqa: ANN001
) -> MagicMock:
    """Mock the HTTP client."""
    return mocker.patch("httpx.AsyncClient.get")


fetch_events_test_cases = [
    ("https://valid.url.com", True),
    (None, True),
    ("https://error.url.com", False),
]


def test_chaturbate_client_initialization() -> None:
    """Test ChaturbateClient initialization."""
    # Test successful initialization
    client = ChaturbateClient(USERNAME, TOKEN)
    assert client.username == USERNAME, "Client username not set correctly."  # noqa: S101
    assert client.token == TOKEN, "Client token not set correctly."  # noqa: S101

    # Test initialization failure with missing username or token
    with pytest.raises(
        ValueError, match="Chaturbate username and token are required."
    ) as exc_info:
        ChaturbateClient("", TOKEN)
    assert "username and token are required" in str(  # noqa: S101
        exc_info.value
    ), "Missing username should raise a ValueError."

    with pytest.raises(
        ValueError, match="Chaturbate username and token are required."
    ) as exc_info:
        ChaturbateClient(USERNAME, "")
    assert "username and token are required" in str(  # noqa: S101
        exc_info.value
    ), "Missing token should raise a ValueError."

    assert not client.client.is_closed, "Client should not be closed after init."  # noqa: S101


@pytest.mark.asyncio()
async def test_http_client_re_opened_directly(mocker) -> None:  # noqa: ANN001
    """Test that the HTTP client is re-opened when it is closed."""
    client = ChaturbateClient("username", "token")
    mocker.patch.object(
        AsyncClient, "is_closed", new_callable=MagicMock, return_value=True
    )
    mock_debug = mocker.patch("chaturbate_poller.chaturbate_poller.logger.debug")
    mocker.patch("chaturbate_poller.chaturbate_poller.httpx.AsyncClient")

    await client.__aenter__()

    mock_debug.assert_any_call("HTTP client re-opened.")
    mock_debug.assert_any_call("Client opened.")


@pytest.mark.asyncio()
@pytest.mark.parametrize(("url", "expected_success"), fetch_events_test_cases)
async def test_fetch_events(url, expected_success, http_client_mock) -> None:  # noqa: ANN001
    """Test fetching events from the Chaturbate API."""
    client = ChaturbateClient(USERNAME, TOKEN)

    mock_response = Response(200, json={"events": [], "nextUrl": ""})
    mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001

    if expected_success:
        http_client_mock.return_value = mock_response
        if url is None:
            url = TEST_URL
        result = await client.fetch_events(url)
        assert isinstance(  # noqa: S101
            result, EventsAPIResponse
        ), "Expected EventsAPIResponse object."
        assert (  # noqa: S101
            http_client_mock.call_count == 1
        ), "Expected one call to httpx.AsyncClient.get."
        assert http_client_mock.call_args[0][0] == url, "Expected URL to match."  # noqa: S101
    else:
        http_client_mock.side_effect = HTTPStatusError(
            message="Error",
            request=Request("GET", "https://error.url.com"),
            response=mock_response,
        )

        with pytest.raises(HTTPStatusError):
            await client.fetch_events(url)


@pytest.mark.asyncio()
async def test_fetch_events_with_timeout(http_client_mock) -> None:  # noqa: ANN001
    """Test fetching events with a timeout."""
    client = ChaturbateClient(USERNAME, TOKEN, timeout=1)

    mock_response = Response(200, json={"events": [], "nextUrl": ""})
    mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001

    http_client_mock.return_value = mock_response

    result = await client.fetch_events(TEST_URL)
    assert isinstance(result, EventsAPIResponse), "Expected EventsAPIResponse object."  # noqa: S101
    assert (  # noqa: S101
        http_client_mock.call_count == 1
    ), "Expected one call to httpx.AsyncClient.get."
    assert http_client_mock.call_args[1]["timeout"] is None, "Expected no timeout."  # noqa: S101


@pytest.mark.parametrize(
    ("exception", "expected_retry"),
    [
        (
            HTTPStatusError(
                message="Server Error",
                request=Request("GET", "https://error.url.com"),
                response=Response(500),
            ),
            True,
        ),  # Retry on 500 status code
        (
            HTTPStatusError(
                message="Client Error",
                request=Request("GET", "https://error.url.com"),
                response=Response(400),
            ),
            False,
        ),  # No retry on 400 status code
    ],
)
def test_need_retry(exception, expected_retry) -> None:  # noqa: ANN001
    """Test need_retry() function."""
    assert (  # noqa: S101
        need_retry(exception) is expected_retry
    ), "need_retry() did not return the expected result."


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "exception",
    [
        RequestError(
            message="Network error", request=Request("GET", "https://test.com")
        ),
    ],
)
async def test_fetch_events_network_failures(exception, http_client_mock) -> None:  # noqa: ANN001
    """Test handling network failures in fetch_events."""
    client = ChaturbateClient(USERNAME, TOKEN)
    http_client_mock.side_effect = exception

    with pytest.raises(RequestError):
        await client.fetch_events(TEST_URL)


@pytest.mark.asyncio()
async def test_fetch_events_malformed_json(http_client_mock) -> None:  # noqa: ANN001
    """Test handling malformed JSON in fetch_events."""
    client = ChaturbateClient(USERNAME, TOKEN)
    request_obj = Request("GET", "https://test.com")

    mock_response = Response(200, content=b"{not: 'json'}")
    mock_response._request = request_obj  # noqa: SLF001

    http_client_mock.return_value = mock_response

    with pytest.raises(JSONDecodeError):
        await client.fetch_events(TEST_URL)


@pytest.mark.asyncio()
async def test_complete_event_flow(http_client_mock) -> None:  # noqa: ANN001
    """Test complete event flow."""
    client = ChaturbateClient(USERNAME, TOKEN)
    event_data = {
        "events": [
            {
                "method": "userEnter",
                "object": {
                    "user": {
                        "username": "fan_user",
                        "inFanclub": True,
                        "hasTokens": True,
                        "isMod": False,
                        "gender": "m",
                        "recentTips": "none",
                    }
                },
                "id": "event_id_1",
            }
        ],
        "nextUrl": TEST_URL,
    }

    mock_response = Response(200, json=event_data)
    mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001
    http_client_mock.return_value = mock_response

    response = await client.fetch_events()
    assert len(response.events) == 1, "Expected one event."  # noqa: S101

    # Ensure that `object` and `user` are not None before accessing `username`
    first_event_object_user = (
        response.events[0].object.user if response.events[0].object else None
    )
    assert first_event_object_user is not None, "User object is None."  # noqa: S101
    assert (  # noqa: S101
        first_event_object_user.username == "fan_user"
    ), "Event user does not match."


@pytest.mark.asyncio()
async def test_timeout_handling(http_client_mock) -> None:  # noqa: ANN001
    """Test handling of timeouts in fetch_events."""
    client = ChaturbateClient(USERNAME, TOKEN, timeout=1)
    http_client_mock.side_effect = TimeoutException(message="Timeout", request=None)

    with pytest.raises(TimeoutException):
        await client.fetch_events(TEST_URL)


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("status_code", "should_succeed"),
    [
        (200, True),
        (404, False),
        (500, False),
    ],
)
async def test_fetch_events_http_statuses(
    status_code,  # noqa: ANN001
    should_succeed,  # noqa: ANN001
    http_client_mock,  # noqa: ANN001
) -> None:
    """Test handling of different HTTP statuses in fetch_events."""
    client = ChaturbateClient(USERNAME, TOKEN)

    mock_response = Response(status_code, json={"events": [], "nextUrl": ""})
    mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001
    http_client_mock.return_value = mock_response

    if should_succeed:
        result = await client.fetch_events(TEST_URL)
        assert isinstance(  # noqa: S101
            result, EventsAPIResponse
        ), "Expected EventsAPIResponse object for 200 response."
    else:
        with pytest.raises(HTTPStatusError):
            await client.fetch_events(TEST_URL)
