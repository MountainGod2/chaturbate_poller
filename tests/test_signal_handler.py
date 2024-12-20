import asyncio
import signal
from typing import Any

import pytest

from chaturbate_poller.signal_handler import SignalHandler


class TestSignalHandler:
    """Tests for the signal handler."""

    @pytest.mark.asyncio
    async def test_signal_handler_initialization(
        self,
        signal_handler: SignalHandler,
        stop_future: asyncio.Future[None],
    ) -> None:
        """Test the initialization of the SignalHandler class."""
        event_loop = asyncio.get_running_loop()
        assert signal_handler.loop is event_loop
        assert signal_handler.stop_future is stop_future

    @pytest.mark.asyncio
    async def test_signal_handler_setup_non_windows(
        self,
        signal_handler: SignalHandler,
        mocker: Any,
    ) -> None:
        """Test the setup method of the SignalHandler class on non-Windows platforms."""
        event_loop = asyncio.get_running_loop()
        mocker.patch("sys.platform", "linux")
        mock_add_signal_handler = mocker.patch.object(event_loop, "add_signal_handler")
        await signal_handler.setup()
        mock_add_signal_handler.assert_any_call(signal.SIGINT, mocker.ANY)
        mock_add_signal_handler.assert_any_call(signal.SIGTERM, mocker.ANY)
        assert mock_add_signal_handler.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_signal(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the handle_signal method of the SignalHandler class."""
        # Directly test handle_signal to ensure it calls shutdown when stop_future is not done
        mock_shutdown = mocker.patch.object(signal_handler, "_shutdown")
        await signal_handler.handle_signal(signal.SIGINT)
        mock_shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_signal_future_done(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None], mocker: Any
    ) -> None:
        """Test the handle_signal method when the future is already done."""
        mocker.patch.object(stop_future, "done", return_value=True)
        mock_shutdown = mocker.patch.object(signal_handler, "_shutdown")
        await signal_handler.handle_signal(signal.SIGINT)
        mock_shutdown.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _shutdown method of the SignalHandler class."""
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        await signal_handler._shutdown()
        assert signal_handler.stop_future.done()
        mock_cancel_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_tasks(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test the _cancel_tasks method of the SignalHandler class."""
        task1 = asyncio.create_task(asyncio.sleep(1))
        task2 = asyncio.create_task(asyncio.sleep(1))
        mocker.patch("asyncio.all_tasks", return_value={task1, task2})
        await signal_handler._cancel_tasks()
        assert task1.cancelled()
        assert task2.cancelled()
        for task in [task1, task2]:
            if not task.done():
                await task

    @pytest.mark.asyncio
    async def test_shutdown_logging(self, signal_handler: SignalHandler, mocker: Any) -> None:
        """Test logging during the _shutdown method."""
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        await signal_handler._shutdown()
        mock_cancel_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_future_already_done(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None], mocker: Any
    ) -> None:
        """Test the _shutdown method when stop_future is already done."""
        stop_future.set_result(None)
        mock_cancel_tasks = mocker.patch.object(signal_handler, "_cancel_tasks")
        await signal_handler._shutdown()
        mock_cancel_tasks.assert_not_called()

    @pytest.mark.asyncio
    async def test_signal_handler_setup_runs_once(
        self,
        signal_handler: SignalHandler,
    ) -> None:
        """Test that setup can only be called once."""
        await signal_handler.setup()
        assert signal_handler._is_setup
        with pytest.raises(RuntimeError):
            await signal_handler.setup()

    @pytest.mark.asyncio
    async def test_signal_handler_setup_logging(
        self,
        signal_handler: SignalHandler,
        mocker: Any,
    ) -> None:
        """Test logging during the setup method."""
        mock_add_signal_handler = mocker.patch.object(signal_handler.loop, "add_signal_handler")
        await signal_handler.setup()
        assert mock_add_signal_handler.call_count == 2
        mock_add_signal_handler.assert_any_call(signal.SIGINT, mocker.ANY)
        mock_add_signal_handler.assert_any_call(signal.SIGTERM, mocker.ANY)
        assert signal_handler._is_setup
