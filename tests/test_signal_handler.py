import asyncio
import re
import signal

import pytest
from pytest_mock import MockerFixture

from chaturbate_poller.utils.signal_handler import SignalHandler


class TestSignalHandler:
    """Tests for signal handling."""

    @pytest.mark.asyncio
    async def test_initialization(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None]
    ) -> None:
        """Test initialization of SignalHandler."""
        assert signal_handler.loop is asyncio.get_running_loop()
        assert signal_handler.stop_future is stop_future

    @pytest.mark.asyncio
    async def test_setup(self, signal_handler: SignalHandler, mocker: MockerFixture) -> None:
        """Test setup of SignalHandler on non-Windows platforms."""
        mocker.patch("sys.platform", "linux")
        mock_add_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "add_signal_handler"
        )
        await signal_handler.setup()
        mock_add_signal_handler.assert_any_call(signal.SIGINT, mocker.ANY)
        mock_add_signal_handler.assert_any_call(signal.SIGTERM, mocker.ANY)

    @pytest.mark.asyncio
    async def test_setup_windows(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test setup of SignalHandler on Windows platform."""
        mocker.patch("sys.platform", "win32")
        mock_add_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "add_signal_handler"
        )
        await signal_handler.setup()
        mock_add_signal_handler.assert_called_with(signal.SIGTERM, mocker.ANY)

    @pytest.mark.asyncio
    async def test_setup_already_setup(self, signal_handler: SignalHandler) -> None:
        """Test that calling setup twice raises RuntimeError."""
        await signal_handler.setup()
        with pytest.raises(
            RuntimeError, match=re.escape("SignalHandler.setup() has already been called.")
        ):
            await signal_handler.setup()

    @pytest.mark.asyncio
    async def test_handle_signal(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test handle_signal calls shutdown when future is not done."""
        mock_shutdown = mocker.patch.object(signal_handler, "_shutdown")
        await signal_handler.handle_signal(signal.SIGINT)
        mock_shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_signal_future_already_done(
        self,
        signal_handler: SignalHandler,
        stop_future: asyncio.Future[None],
        mocker: MockerFixture,
    ) -> None:
        """Test handle_signal does not call shutdown when future is already done."""
        stop_future.set_result(None)
        mock_shutdown = mocker.patch.object(signal_handler, "_shutdown")

        await signal_handler.handle_signal(signal.SIGINT)

        mock_shutdown.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_tasks(self, signal_handler: SignalHandler, mocker: MockerFixture) -> None:
        """Test cancellation of tasks during shutdown."""
        task1 = asyncio.create_task(asyncio.sleep(1))
        task2 = asyncio.create_task(asyncio.sleep(1))
        mocker.patch("asyncio.all_tasks", return_value={task1, task2})
        await signal_handler._cancel_tasks()
        assert all(task.cancelled() for task in [task1, task2])

    @pytest.mark.asyncio
    async def test_cancel_tasks_with_timeout(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test task cancellation with slow tasks that exceed timeout."""

        async def slow_task() -> None:
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                await asyncio.sleep(6)
                raise

        task = asyncio.create_task(slow_task())
        mocker.patch("asyncio.all_tasks", return_value={task})

        await signal_handler._cancel_tasks()
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_cancel_tasks_with_exceptions(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test task cancellation when tasks raise exceptions during cleanup."""

        async def failing_task() -> None:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                msg = "Task cleanup failed"
                raise RuntimeError(msg) from None

        task = asyncio.create_task(failing_task())
        mocker.patch("asyncio.all_tasks", return_value={task})

        await signal_handler._cancel_tasks()
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_shutdown_idempotent(
        self, signal_handler: SignalHandler, stop_future: asyncio.Future[None]
    ) -> None:
        """Test that multiple shutdown calls are handled correctly."""
        await signal_handler._shutdown()
        assert stop_future.done()

        await signal_handler._shutdown()
        assert stop_future.done()
