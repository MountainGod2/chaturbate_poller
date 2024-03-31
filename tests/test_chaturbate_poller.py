"""Tests for the chaturbate_poller module."""

from json import JSONDecodeError

import pytest
from chaturbate_poller.chaturbate_poller import ChaturbateClient, need_retry
from chaturbate_poller.models import EventsAPIResponse
from httpx import HTTPStatusError, Request, RequestError, Response, TimeoutException

USERNAME = "testuser"
TOKEN = "testtoken"  # noqa: S105
TEST_URL = "https://events.testbed.cb.dev/events/testuser/testtoken/"

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

    # Check if the client is closed after initialization
    assert not client.client.is_closed, "Client should not be closed after init."  # noqa: S101


@pytest.mark.asyncio()
@pytest.mark.parametrize(("url", "expected_success"), fetch_events_test_cases)
async def test_fetch_events(url, expected_success, mocker) -> None:  # noqa: ANN001
    """Test fetching events from the Chaturbate API."""
    async with ChaturbateClient(USERNAME, TOKEN) as client:
        mock_get = mocker.patch("httpx.AsyncClient.get")

        mock_response = Response(200, json={"events": [], "nextUrl": ""})
        mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001

        if expected_success:
            mock_get.return_value = mock_response

            if url is None:
                url = TEST_URL
            result = await client.fetch_events(url)
            assert isinstance(  # noqa: S101
                result, EventsAPIResponse
            ), "Expected EventsAPIResponse object."
            assert (  # noqa: S101
                mock_get.call_count == 1
            ), "Expected one call to httpx.AsyncClient.get."

            assert mock_get.call_args[0][0] == url, "Expected URL to match."  # noqa: S101
        else:
            mock_get.side_effect = HTTPStatusError(
                message="Error",
                request=Request("GET", "https://error.url.com"),
                response=mock_response,
            )

            with pytest.raises(HTTPStatusError):
                await client.fetch_events(url)


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
async def test_fetch_events_network_failures(exception, mocker) -> None:  # noqa: ANN001
    """Test handling network failures in fetch_events."""
    async with ChaturbateClient(USERNAME, TOKEN) as client:
        mocker.patch("httpx.AsyncClient.get", side_effect=exception)

        with pytest.raises(RequestError):
            await client.fetch_events(TEST_URL)


@pytest.mark.asyncio()
async def test_fetch_events_malformed_json(mocker) -> None:  # noqa: ANN001
    """Test handling malformed JSON in fetch_events."""
    async with ChaturbateClient(USERNAME, TOKEN) as client:
        request_obj = Request("GET", "https://test.com")

        mock_response = Response(200, content=b"{not: 'json'}")
        mock_response._request = request_obj  # noqa: SLF001

        mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

        with pytest.raises(JSONDecodeError):
            await client.fetch_events(TEST_URL)


@pytest.mark.asyncio()
async def test_complete_event_flow(mocker) -> None:  # noqa: ANN001
    """Test complete event flow."""
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

    async with ChaturbateClient(USERNAME, TOKEN) as client:
        request_obj = Request("GET", "https://test.com")
        mock_response = Response(200, json=event_data)
        mock_response._request = request_obj  # noqa: SLF001
        mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

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
async def test_timeout_handling(mocker) -> None:  # noqa: ANN001
    """Test handling of timeouts in fetch_events."""
    async with ChaturbateClient(USERNAME, TOKEN, timeout=1) as client:
        mocker.patch(
            "httpx.AsyncClient.get",
            side_effect=TimeoutException(message="Timeout", request=None),
        )

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
async def test_fetch_events_http_statuses(status_code, should_succeed, mocker) -> None:  # noqa: ANN001
    """Test handling of different HTTP statuses in fetch_events."""
    async with ChaturbateClient(USERNAME, TOKEN) as client:
        mock_get = mocker.patch("httpx.AsyncClient.get")
        mock_response = Response(status_code, json={"events": [], "nextUrl": ""})
        mock_response._request = Request("GET", "https://test.com")  # noqa: SLF001
        mock_get.return_value = mock_response

        if should_succeed:
            result = await client.fetch_events(TEST_URL)
            assert isinstance(  # noqa: S101
                result, EventsAPIResponse
            ), "Expected EventsAPIResponse object for 200 response."
        else:
            with pytest.raises(HTTPStatusError):
                await client.fetch_events(TEST_URL)
