# ruff: noqa: S101, S603
"""Tests for the __main__ module."""

import asyncio
import logging
from contextlib import suppress
from unittest.mock import AsyncMock

import pytest

from chaturbate_poller.__main__ import start_polling
from chaturbate_poller.chaturbate_client import ChaturbateClient


def test_start_polling_verbose(mocker) -> None:  # noqa: ANN001
    """Test the start_polling function with verbose output."""
    with (  # noqa: PT012
        suppress(KeyboardInterrupt),
        pytest.raises(ValueError, match="Unauthorized access. Verify the username and token."),
    ):
        asyncio.run(
            start_polling(
                "username", "token", 10, event_handler=mocker.Mock(), testbed=False, verbose=True
            )
        )

        assert logging.getLogger().level == logging.DEBUG


@pytest.mark.asyncio
async def test_fetch_events_returns_none(mocker) -> None:  # noqa: ANN001
    """Test start_polling when fetch_events returns None."""
    mocker.patch.dict("os.environ", {"CB_USERNAME": "testuser", "CB_TOKEN": "testtoken"})

    mock_fetch_events = AsyncMock(return_value=None)

    mock_client = mocker.patch.object(ChaturbateClient, "__aenter__", return_value=mocker.Mock())
    mock_client.return_value.fetch_events = mock_fetch_events

    await start_polling(
        username="testuser",
        token="testtoken",  # noqa: S106
        api_timeout=10,
        event_handler=mocker.Mock(),
        testbed=False,
        verbose=False,
    )

    mock_fetch_events.assert_called_once()


@pytest.mark.asyncio
async def test_missing_username_or_token(mocker, caplog) -> None:  # noqa: ANN001
    """Test start_polling when username or token is missing."""
    mocker.patch.dict("os.environ", {"CB_USERNAME": "", "CB_TOKEN": ""})

    with caplog.at_level(logging.ERROR):
        await start_polling(
            username="",
            token="",
            api_timeout=10,
            testbed=False,
            verbose=False,
            event_handler=mocker.Mock(),
        )

    assert (
        "CB_USERNAME and CB_TOKEN must be provided as arguments or environment variables."
        in caplog.text
    )
