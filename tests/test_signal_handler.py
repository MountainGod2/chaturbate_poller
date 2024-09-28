"""Tests for the SignalHandler class."""

import asyncio
import logging
import signal
import sys
from unittest import mock

import pytest

from chaturbate_poller.signal_handler import SignalHandler


@pytest.fixture
def stop_future(event_loop: asyncio.AbstractEventLoop) -> asyncio.Future[None]:
    """Create a future to set when the signal is received."""
    return event_loop.create_future()


@pytest.fixture
def signal_handler(
    event_loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]
) -> SignalHandler:
    """Create an instance of the SignalHandler class."""
    return SignalHandler(event_loop, stop_future)


def test_signal_handler_initialization(signal_handler: SignalHandler) -> None:
    """Test the initialization of the SignalHandler class."""
    assert isinstance(signal_handler.logger, logging.Logger)
    assert signal_handler.loop is not None
    assert signal_handler.stop_future is not None


def test_signal_handler_setup(
    signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop
) -> None:
    """Test the setup method of the SignalHandler class."""
    with mock.patch.object(event_loop, "add_signal_handler") as mock_add_signal_handler:
        signal_handler.setup()
        if sys.platform != "win32":
            mock_add_signal_handler.assert_any_call(
                signal.SIGINT, signal_handler.handle_signal, signal.SIGINT
            )
            mock_add_signal_handler.assert_any_call(
                signal.SIGTERM, signal_handler.handle_signal, signal.SIGTERM
            )
        else:
            signal_handler.logger.warning.assert_called_with(
                "Signal handlers not supported on this platform."
            )


def test_handle_signal(signal_handler: SignalHandler, stop_future: asyncio.Future[None]) -> None:
    """Test the handle_signal method of the SignalHandler class."""
    with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
        signal_handler.handle_signal(signal.SIGINT)
        if not stop_future.done():
            mock_create_task.assert_called_once()


@pytest.mark.asyncio
async def test_shutdown(signal_handler: SignalHandler) -> None:
    """Test the _shutdown method of the SignalHandler class."""
    with mock.patch.object(signal_handler, "_cancel_tasks") as mock_cancel_tasks:
        shutdown_task = await signal_handler._shutdown()  # type: ignore[func-returns-value]
        assert shutdown_task is None
        mock_cancel_tasks.assert_called_once()
        assert signal_handler.stop_future.done()


@pytest.mark.asyncio
async def test_cancel_tasks(signal_handler: SignalHandler) -> None:
    """Test the _cancel_tasks method of the SignalHandler class."""
    current_task = asyncio.current_task()
    tasks = [asyncio.create_task(asyncio.sleep(1)) for _ in range(3)]
    await asyncio.sleep(0)  # Let the tasks start

    with mock.patch("asyncio.all_tasks", return_value=[*tasks, current_task]):
        await signal_handler._cancel_tasks()
        for task in tasks:
            assert task.cancelled()
