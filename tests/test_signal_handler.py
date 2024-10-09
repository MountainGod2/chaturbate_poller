import asyncio
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
        assert signal_handler.loop is event_loop
        assert signal_handler.stop_future is stop_future

    def test_signal_handler_setup_non_windows(
        self,
        signal_handler: SignalHandler,
        event_loop: asyncio.AbstractEventLoop,
        mocker: Any,
    ) -> None:
        """Test the setup method of the SignalHandler class on non-Windows platforms."""
        mocker.patch("sys.platform", "linux")
        mock_add_signal_handler = mocker.patch.object(event_loop, "add_signal_handler")
        signal_handler.setup()
        mock_add_signal_handler.assert_any_call(
            signal.SIGINT, signal_handler.handle_signal, signal.SIGINT
        )
        mock_add_signal_handler.assert_any_call(
            signal.SIGTERM, signal_handler.handle_signal, signal.SIGTERM
        )
        assert mock_add_signal_handler.call_count == 2

    def test_signal_handler_setup_windows(
        self, signal_handler: SignalHandler, event_loop: asyncio.AbstractEventLoop, mocker: Any
    ) -> None:
        """Test the setup method of the SignalHandler class on Windows platforms."""
        mocker.patch("sys.platform", "win32")
        signal_handler.setup()
        mock_add_signal_handler = mocker.patch.object(event_loop, "add_signal_handler")
        mock_add_signal_handler.assert_not_called()

    def test_handle_signal(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the handle_signal method of the SignalHandler class."""
        mock_create_task = mocker.patch.object(signal_handler.loop, "create_task")
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_called_once()

    def test_handle_signal_future_done(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None], mocker: Any
    ) -> None:
        """Test the handle_signal method when the future is already done."""
        mocker.patch.object(stop_future, "done", return_value=True)
        mock_create_task = mocker.patch.object(signal_handler.loop, "create_task")
        signal_handler.handle_signal(signal.SIGINT)
        mock_create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _shutdown method of the SignalHandler class."""
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        shutdown = signal_handler._shutdown()
        await shutdown
        assert signal_handler.stop_future.done()
        mock_cancel_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_tasks(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _cancel_tasks method of the SignalHandler class."""
        current_task = asyncio.current_task()
        tasks = [asyncio.create_task(asyncio.sleep(1)) for _ in range(3)]
        await asyncio.sleep(0)
        mocker.patch.object(signal_handler, "_shutdown", return_value=asyncio.Future())
        mocker.patch("asyncio.all_tasks", return_value=[*tasks, current_task])
        cancel_tasks = signal_handler._cancel_tasks()
        await cancel_tasks
        for task in tasks:
            assert task.cancelled()
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
        await signal_handler._cancel_tasks()
        assert task1.cancelled()
        assert task2.cancelled()

    def test_shutdown_logging(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test logging during the _shutdown method."""
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        asyncio.run(signal_handler._shutdown())
        mock_cancel_tasks.assert_called_once()
