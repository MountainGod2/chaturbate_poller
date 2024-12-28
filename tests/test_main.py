import asyncio
from contextlib import suppress

import pytest
from pytest_mock import MockerFixture

from chaturbate_poller.exceptions import AuthenticationError
from chaturbate_poller.main import main, start_polling


class TestMain:
    """Tests for the main module."""

    @pytest.mark.asyncio
    async def test_start_polling_success(self, mocker: MockerFixture) -> None:
        """Test successful polling process."""
        mock_client = mocker.AsyncMock()
        mock_event_handler = mocker.AsyncMock()

        response1 = mocker.Mock(events=[mocker.Mock(), mocker.Mock()], next_url="next_url")
        response2 = mocker.Mock(events=[mocker.Mock()], next_url=None)
        mock_client.fetch_events = mocker.AsyncMock(side_effect=[response1, response2])

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        await start_polling(
            username="test_user",
            token="test_token",  # noqa: S106
            api_timeout=10,
            event_handler=mock_event_handler,
            testbed=False,
        )

        assert mock_client.fetch_events.await_args_list == [
            mocker.call(None),
            mocker.call("next_url"),
        ]

        assert mock_event_handler.handle_event.call_count == 3

    @pytest.mark.asyncio
    async def test_main_success(self, mocker: MockerFixture) -> None:
        """Test successful execution of main function."""
        mock_event_handler = mocker.Mock()
        mock_signal_handler = mocker.AsyncMock()
        mocker.patch("chaturbate_poller.main.create_event_handler", return_value=mock_event_handler)
        mocker.patch("chaturbate_poller.main.SignalHandler", return_value=mock_signal_handler)

        mock_start_polling = mocker.patch("chaturbate_poller.main.start_polling", return_value=None)

        stop_future: asyncio.Future[None] = asyncio.Future()
        stop_future.set_result(None)
        mocker.patch("asyncio.Future", return_value=stop_future)

        with suppress(asyncio.CancelledError):
            await main(
                username="test_user",
                token="test_token",  # noqa: S106
                api_timeout=10,
                testbed=False,
                verbose=True,
                use_database=True,
            )

        mock_signal_handler.setup.assert_called_once()
        mock_start_polling.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_polling_authentication_error(self, mocker: MockerFixture) -> None:
        """Test polling process with authentication error."""
        mock_client = mocker.AsyncMock()
        mock_client.fetch_events.side_effect = AuthenticationError("Invalid token")

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        with pytest.raises(AuthenticationError, match="Invalid token"):
            await start_polling(
                username="test_user",
                token="invalid_token",  # noqa: S106
                api_timeout=10,
                event_handler=mocker.Mock(),
                testbed=False,
            )

    @pytest.mark.asyncio
    async def test_main_authentication_error(self, mocker: MockerFixture) -> None:
        """Test main function with authentication error."""
        mock_client = mocker.AsyncMock()
        mock_client.fetch_events.side_effect = AuthenticationError("Invalid token")

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        with pytest.raises(AuthenticationError, match="Invalid token"):
            await main(
                username="test_user",
                token="invalid_token",  # noqa: S106
                api_timeout=10,
                testbed=False,
                verbose=True,
                use_database=True,
            )

    @pytest.mark.asyncio
    async def test_main_missing_username_and_token(self, mocker: MockerFixture) -> None:
        """Test main function with missing username and token."""
        mock_client = mocker.AsyncMock()
        mock_client.fetch_events.side_effect = AuthenticationError("Invalid token")

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        with pytest.raises(ValueError, match="Username and token are required"):
            await main(
                username="",
                token="",
                api_timeout=-1,
                testbed=False,
                verbose=True,
                use_database=True,
            )

    @pytest.mark.asyncio
    async def test_start_polling_breaks_on_empty_response(self, mocker: MockerFixture) -> None:
        """Test polling process breaks on empty response."""
        mock_client = mocker.AsyncMock()
        mock_event_handler = mocker.AsyncMock()

        mock_client.fetch_events = mocker.AsyncMock(return_value=None)

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        await start_polling(
            username="test_user",
            token="test_token",  # noqa: S106
            api_timeout=10,
            event_handler=mock_event_handler,
            testbed=False,
        )

        mock_client.fetch_events.assert_called_once_with(None)
        mock_event_handler.handle_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_polling_breaks_on_empty_events(self, mocker: MockerFixture) -> None:
        """Test polling process breaks on empty events list."""
        mock_client = mocker.AsyncMock()
        mock_event_handler = mocker.AsyncMock()

        mock_response = mocker.Mock()
        mock_response.events = []
        mock_response.next_url = None
        mock_client.fetch_events = mocker.AsyncMock(return_value=mock_response)

        mock_context = mocker.AsyncMock()
        mock_context.__aenter__.return_value = mock_client
        mocker.patch("chaturbate_poller.main.ChaturbateClient", return_value=mock_context)

        await start_polling(
            username="test_user",
            token="test_token",  # noqa: S106
            api_timeout=10,
            event_handler=mock_event_handler,
            testbed=False,
        )

        mock_client.fetch_events.assert_called_once_with(None)
        mock_event_handler.handle_event.assert_not_called()
