"""Tests for the SignalHandler class."""

import asyncio
import logging
import signal
import sys
from typing import Never  # noqa: F401
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


def test_signal_handler_initialization(
    signal_handler: SignalHandler,
    event_loop: asyncio.AbstractEventLoop,
    stop_future: asyncio.Future[None],
) -> None:
    """Test the initialization of the SignalHandler class."""
    assert isinstance(signal_handler.logger, logging.Logger)
    assert signal_handler.loop is event_loop
    assert signal_handler.stop_future is stop_future


def test_signal_handler_setup_non_windows(
    signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop
) -> None:
    """Test the setup method of the SignalHandler class on non-Windows platforms."""
    with mock.patch.object(sys, "platform", "linux"):  # noqa: SIM117
        with mock.patch.object(event_loop, "add_signal_handler") as mock_add_signal_handler:
            with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
                signal_handler.setup()
                mock_add_signal_handler.assert_any_call(
                    signal.SIGINT, signal_handler.handle_signal, signal.SIGINT
                )
                mock_add_signal_handler.assert_any_call(
                    signal.SIGTERM, signal_handler.handle_signal, signal.SIGTERM
                )
                mock_logger_debug.assert_called_with(
                    "Signal handlers set up for SIGINT and SIGTERM."
                )


def test_signal_handler_setup_windows(
    signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop
) -> None:
    """Test the setup method of the SignalHandler class on Windows platforms."""
    with mock.patch.object(sys, "platform", "win32"):  # noqa: SIM117
        with mock.patch.object(signal_handler.logger, "warning") as mock_logger_warning:
            signal_handler.setup()
            mock_logger_warning.assert_called_once_with(
                "Signal handlers not supported on this platform."
            )
            # Ensure that add_signal_handler is not called
            with mock.patch.object(event_loop, "add_signal_handler") as mock_add_signal_handler:
                mock_add_signal_handler.assert_not_called()


def test_handle_signal(signal_handler: SignalHandler) -> None:
    """Test the handle_signal method of the SignalHandler class."""
    with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:  # noqa: SIM117
        with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
            signal_handler.handle_signal(signal.SIGINT)
            mock_create_task.assert_called_once()
            mock_logger_debug.assert_called_with(
                "Received signal %s. Initiating shutdown.", signal.SIGINT.name
            )


def test_handle_signal_various_signals(signal_handler: SignalHandler) -> None:
    """Test handle_signal with different signals."""
    with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
        # Test SIGINT
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_called_once()
        mock_create_task.reset_mock()

        # Test SIGTERM
        signal_handler.handle_signal(signal.SIGTERM)
        mock_create_task.assert_called_once()


def test_handle_signal_future_done(
    signal_handler: SignalHandler, stop_future: asyncio.Future[None]
) -> None:
    """Test handle_signal when the stop_future is already done."""
    stop_future.set_result(None)  # Mark the future as done

    with mock.patch.object(signal_handler.loop, "create_task") as mock_create_task:
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_not_called()  # Ensure shutdown is not triggered


@pytest.mark.asyncio
async def test_shutdown(signal_handler: SignalHandler) -> None:
    """Test the _shutdown method of the SignalHandler class."""
    with mock.patch.object(signal_handler, "_cancel_tasks") as mock_cancel_tasks:  # noqa: SIM117
        with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
            await signal_handler._shutdown()  # type: ignore[func-returns-value]
            assert signal_handler.stop_future.done()
            mock_cancel_tasks.assert_called_once()
            mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")


@pytest.mark.asyncio
async def test_cancel_tasks(signal_handler: SignalHandler) -> None:
    """Test the _cancel_tasks method of the SignalHandler class."""
    current_task = asyncio.current_task()
    tasks = [asyncio.create_task(asyncio.sleep(1)) for _ in range(3)]
    await asyncio.sleep(0)  # Let the tasks start

    with mock.patch("asyncio.all_tasks", return_value=[*tasks, current_task]):  # noqa: SIM117
        with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:
            await signal_handler._cancel_tasks()
            for task in tasks:
                assert task.cancelled()

            mock_logger_debug.assert_called_with("All tasks cancelled and cleaned up.")


def test_shutdown_logging(signal_handler: SignalHandler) -> None:
    """Test logging during the _shutdown method."""
    with mock.patch.object(signal_handler.logger, "debug") as mock_logger_debug:  # noqa: SIM117
        with mock.patch.object(signal_handler, "_cancel_tasks"):
            # Since _shutdown is async, we need to run it in an event loop
            asyncio.run(signal_handler._shutdown())
            mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")
