"""Tests for the main module."""

import asyncio
import contextlib
import signal
import subprocess
import time
from unittest.mock import AsyncMock

import httpx
import pytest
from chaturbate_poller.__main__ import main
from pytest_mock import MockerFixture


@pytest.mark.asyncio()
async def test_successful_event_fetching(mocker: MockerFixture) -> None:
    """Test successful event fetching."""
    # Setup environment variables
    mocker.patch("os.getenv", side_effect=lambda: "test_value")
    # Mock the ChaturbateClient and its method
    mock_client_class = mocker.patch("chaturbate_poller.__main__.ChaturbateClient")
    mock_client_instance = mock_client_class.return_value.__aenter__.return_value
    mock_client_instance.fetch_events.side_effect = [
        AsyncMock(events=["event1", "event2"]),
        asyncio.CancelledError,
    ]
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.info")

    contextlib.suppress(asyncio.CancelledError)
    await main()

    # Ensure events are logged
    assert logger_mock.call_count >= 2  # noqa: S101, PLR2004


@pytest.mark.asyncio()
async def test_http_error_handling(mocker: MockerFixture) -> None:
    """Test HTTP error handling."""
    mocker.patch("os.getenv", side_effect=lambda: "test_value")
    mock_client_class = mocker.patch("chaturbate_poller.__main__.ChaturbateClient")
    mock_client_instance = mock_client_class.return_value.__aenter__.return_value
    mock_client_instance.fetch_events.side_effect = httpx.HTTPError("Error")
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.warning")

    await main()

    logger_mock.assert_called_once_with("Error fetching Chaturbate events.")


@pytest.mark.asyncio()
async def test_keyboard_interrupt_handling(mocker: MockerFixture) -> None:
    """Test KeyboardInterrupt handling."""
    mocker.patch("os.getenv", side_effect=lambda: "test_value")
    mock_client_class = mocker.patch("chaturbate_poller.__main__.ChaturbateClient")
    mock_client_instance = mock_client_class.return_value.__aenter__.return_value
    mock_client_instance.fetch_events.side_effect = asyncio.CancelledError
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.debug")

    await main()

    logger_mock.assert_called_once_with("Cancelled fetching Chaturbate events.")

# Test the main module in a subprocess
def test_main_subprocess() -> None:
    """Test the main module in a subprocess."""
    cmd = [".venv/bin/python", "-m", "chaturbate_poller"]
    process = subprocess.Popen(cmd)  # noqa: S603
    time.sleep(2)
    process.send_signal(signal.SIGINT)
    process.wait()
    assert process.returncode == 0  # noqa: S101


