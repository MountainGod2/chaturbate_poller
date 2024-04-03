"""Tests for the main module."""

import asyncio
import logging
import signal
import subprocess
import time
from unittest.mock import AsyncMock

import httpx
import pytest
from chaturbate_poller.__main__ import main


@pytest.mark.asyncio()
async def test_successful_event_fetching(mocker) -> None:  # noqa: ANN001
    """Test successful event fetching."""
    mocker.patch("os.getenv", return_value="test_value")
    mock_client_class = mocker.patch("chaturbate_poller.__main__.ChaturbateClient")
    mock_client_instance = mock_client_class.return_value.__aenter__.return_value
    mock_client_instance.fetch_events.side_effect = [
        AsyncMock(events=["event1", "event2"]),
        asyncio.CancelledError,
    ]
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.info")

    await main()

    assert logger_mock.call_count >= 2  # noqa: PLR2004, S101


@pytest.mark.asyncio()
async def test_http_error_handling(mocker) -> None:  # noqa: ANN001
    """Test handling of HTTP errors."""
    mocker.patch("os.getenv", return_value="test_value")
    mocker.patch(
        "chaturbate_poller.__main__.ChaturbateClient.fetch_events",
        side_effect=httpx.HTTPError("Error"),
    )
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.warning")

    await main()

    logger_mock.assert_called_once_with("Error fetching Chaturbate events.")


@pytest.mark.asyncio()
async def test_keyboard_interrupt_handling(mocker) -> None:  # noqa: ANN001
    """Test handling of KeyboardInterrupt."""
    mocker.patch("os.getenv", return_value="test_value")
    mocker.patch(
        "chaturbate_poller.__main__.ChaturbateClient.fetch_events",
        side_effect=asyncio.CancelledError,
    )
    logger_mock = mocker.patch("chaturbate_poller.__main__.logger.debug")

    await main()

    logger_mock.assert_any_call("Cancelled fetching Chaturbate events.")


def test_main_subprocess() -> None:
    """Test the main module in a subprocess with improved error handling."""
    cmd = [".venv/bin/python", "-m", "chaturbate_poller"]
    process = subprocess.Popen(
        cmd,  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(5)
    process.send_signal(signal.SIGINT)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        logging.error("STDOUT:\n%s", stdout.decode())
        logging.error("STDERR:\n%s", stderr.decode())
    assert process.returncode == 0, "Subprocess did not exit cleanly."  # noqa: S101
