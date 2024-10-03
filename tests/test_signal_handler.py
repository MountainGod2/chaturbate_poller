import asyncio
import logging
import signal
from typing import Any

import pytest

from chaturbate_poller.signal_handler import SignalHandler


class TestSignalHandler:
    """Tests for the signal handler."""

    def test_signal_handler_initialization(
        self,
        signal_handler: SignalHandler,
        event_loop: asyncio.AbstractEventLoop,
        stop_future: asyncio.Future[None],
    ) -> None:
        """Test the initialization of the SignalHandler class."""
        assert isinstance(signal_handler.logger, logging.Logger)
        assert signal_handler.loop is event_loop
        assert signal_handler.stop_future is stop_future

    def test_signal_handler_setup_non_windows(
        self, signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop, mocker: Any
    ) -> None:
        """Test the setup method of the SignalHandler class on non-Windows platforms."""
        mocker.patch("sys.platform", "linux")
        mock_add_signal_handler = mocker.patch.object(event_loop, "add_signal_handler")
        mock_logger_debug = mocker.patch.object(signal_handler.logger, "debug")
        signal_handler.setup()
        mock_add_signal_handler.assert_any_call(
            signal.SIGINT, signal_handler.handle_signal, signal.SIGINT
        )
        mock_add_signal_handler.assert_any_call(
            signal.SIGTERM, signal_handler.handle_signal, signal.SIGTERM
        )
        mock_logger_debug.assert_called_with("Signal handlers set up for SIGINT and SIGTERM.")

    def test_signal_handler_setup_windows(
        self, signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop, mocker: Any
    ) -> None:
        """Test the setup method of the SignalHandler class on Windows platforms."""
        mocker.patch("sys.platform", "win32")
        mock_logger_warning = mocker.patch.object(signal_handler.logger, "warning")
        signal_handler.setup()
        mock_logger_warning.assert_called_once_with(
            "Signal handlers not supported on this platform."
        )
        mock_add_signal_handler = mocker.patch.object(event_loop, "add_signal_handler")
        mock_add_signal_handler.assert_not_called()

    def test_handle_signal(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the handle_signal method of the SignalHandler class."""
        mock_create_task = mocker.patch.object(signal_handler.loop, "create_task")
        mock_run_until_complete = mocker.patch.object(signal_handler.loop, "run_until_complete")
        mock_logger_debug = mocker.patch.object(signal_handler.logger, "debug")
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_called_once()
        mock_run_until_complete.assert_called_once_with(mock_create_task.return_value)
        mock_logger_debug.assert_called_with(
            "Received signal %s. Initiating shutdown.", signal.SIGINT.name
        )

    def test_handle_signal_future_done(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None], mocker: Any
    ) -> None:
        """Test handle_signal when the stop_future is already done."""
        stop_future.set_result(None)
        mock_create_task = mocker.patch.object(signal_handler.loop, "create_task")
        mock_run_until_complete = mocker.patch.object(signal_handler.loop, "run_until_complete")
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_not_called()
        mock_run_until_complete.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _shutdown method of the SignalHandler class."""
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        mock_logger_debug = mocker.patch.object(signal_handler.logger, "debug")
        shutdown = signal_handler._shutdown()
        await shutdown
        assert signal_handler.stop_future.done()
        mock_cancel_tasks.assert_called_once()
        mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")

    @pytest.mark.asyncio
    async def test_cancel_tasks(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _cancel_tasks method of the SignalHandler class."""
        current_task = asyncio.current_task()
        tasks = [asyncio.create_task(asyncio.sleep(1)) for _ in range(3)]
        await asyncio.sleep(0)
        mocker.patch.object(signal_handler, "_shutdown", return_value=asyncio.Future())
        mocker.patch("asyncio.all_tasks", return_value=[*tasks, current_task])
        mock_logger_debug = mocker.patch.object(signal_handler.logger, "debug")
        cancel_tasks = signal_handler._cancel_tasks()
        await cancel_tasks
        for task in tasks:
            assert task.cancelled()
        mock_logger_debug.assert_called_with("All tasks cancelled and cleaned up.")
        await signal_handler._shutdown()

    @pytest.mark.asyncio
    async def test_cancel_tasks_no_tasks(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test _cancel_tasks method with no tasks."""
        mocker.patch("asyncio.all_tasks", return_value=set())
        await signal_handler._cancel_tasks()

    @pytest.mark.asyncio
    async def test_cancel_tasks_with_tasks(
        self, signal_handler: SignalHandler, mocker: Any
    ) -> None:
        """Test _cancel_tasks method with running tasks."""

        async def dummy_task() -> None:
            await asyncio.sleep(1)

        task1 = asyncio.get_running_loop().create_task(dummy_task())
        task2 = asyncio.get_running_loop().create_task(dummy_task())

        mocker.patch("asyncio.all_tasks", return_value={task1, task2})
        mock_debug = mocker.patch.object(signal_handler.logger, "debug")
        await signal_handler._cancel_tasks()
        mock_debug.assert_any_call("Cancelling %d running task(s)...", 2)
        mock_debug.assert_any_call("All tasks cancelled and cleaned up.")

    def test_shutdown_logging(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test logging during the _shutdown method."""
        mock_logger_debug = mocker.patch.object(signal_handler.logger, "debug")
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        asyncio.run(signal_handler._shutdown())
        mock_logger_debug.assert_any_call("Shutting down tasks and cleaning up.")
        mock_cancel_tasks.assert_called_once()