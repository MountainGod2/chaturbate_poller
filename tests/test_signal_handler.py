"""Tests for SignalHandler class."""

from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING

import pytest

from chaturbate_poller.utils.signal_handler import SignalHandler

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from pytest_mock import MockerFixture


@pytest.fixture
async def signal_handler() -> AsyncGenerator[SignalHandler]:
    """Create a SignalHandler instance for testing."""
    loop = asyncio.get_running_loop()
    stop_future: asyncio.Future[None] = loop.create_future()
    handler = SignalHandler(loop, stop_future)
    yield handler
    handler.cleanup()


class TestSignalHandler:
    """Tests for SignalHandler class."""

    @pytest.mark.asyncio
    async def test_setup(self, signal_handler: SignalHandler, mocker: MockerFixture) -> None:
        """Test setup of SignalHandler."""
        mock_add_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "add_signal_handler"
        )
        await signal_handler.setup()
        mock_add_signal_handler.assert_any_call(
            signal.SIGINT, signal_handler._signal_handler, signal.SIGINT
        )
        mock_add_signal_handler.assert_any_call(
            signal.SIGTERM, signal_handler._signal_handler, signal.SIGTERM
        )

    @pytest.mark.asyncio
    async def test_setup_with_not_implemented_error(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test setup handles NotImplementedError gracefully."""
        mock_add_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "add_signal_handler"
        )
        mock_add_signal_handler.side_effect = NotImplementedError("Signal handling not available")

        await signal_handler.setup()
        # Should still be called but will raise NotImplementedError
        assert mock_add_signal_handler.call_count == 2

    @pytest.mark.asyncio
    async def test_signal_handler_sets_future_result(self, signal_handler: SignalHandler) -> None:
        """Test that _signal_handler sets the stop_future result."""
        # Future should not be done initially
        assert not signal_handler.stop_future.done()

        # Call the signal handler
        signal_handler._signal_handler(signal.SIGINT)

        # Future should now be done
        assert signal_handler.stop_future.done()
        assert signal_handler.stop_future.result() is None

    @pytest.mark.asyncio
    async def test_signal_handler_already_done_future(self, signal_handler: SignalHandler) -> None:
        """Test that _signal_handler handles already done future gracefully."""
        # Set the future result first
        signal_handler.stop_future.set_result(None)
        assert signal_handler.stop_future.done()

        # Call the signal handler - should not raise
        signal_handler._signal_handler(signal.SIGINT)

        # Future should still be done
        assert signal_handler.stop_future.done()

    @pytest.mark.asyncio
    async def test_cleanup(self, signal_handler: SignalHandler, mocker: MockerFixture) -> None:
        """Test cleanup removes signal handlers."""
        mock_remove_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "remove_signal_handler"
        )

        # Setup first to register signals
        await signal_handler.setup()

        # Now cleanup
        signal_handler.cleanup()

        mock_remove_signal_handler.assert_any_call(signal.SIGINT)
        mock_remove_signal_handler.assert_any_call(signal.SIGTERM)

    @pytest.mark.asyncio
    async def test_cleanup_handles_value_error(
        self, signal_handler: SignalHandler, mocker: MockerFixture
    ) -> None:
        """Test cleanup handles ValueError gracefully."""
        mock_remove_signal_handler = mocker.patch.object(
            asyncio.get_running_loop(), "remove_signal_handler"
        )
        mock_remove_signal_handler.side_effect = ValueError("Handler not found")

        # Setup first to register signals
        await signal_handler.setup()

        # Now cleanup - should not raise
        signal_handler.cleanup()

        # Should still be called even though it raises
        assert mock_remove_signal_handler.call_count == 2
