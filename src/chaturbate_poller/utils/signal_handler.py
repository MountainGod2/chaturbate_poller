"""Signal handler for SIGINT and SIGTERM signals."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

logger: logging.Logger = logging.getLogger(name=__name__)
"""logging.Logger: The module-level logger."""


class SignalHandler:
    """Signal handler for SIGINT and SIGTERM signals."""

    def __init__(self, loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]) -> None:
        """Initialize the SignalHandler.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): The future to set when the signal is received.
        """
        self.loop: asyncio.AbstractEventLoop = loop
        self.stop_future: asyncio.Future[None] = stop_future
        self._is_setup: bool = False
        logger.debug("SignalHandler initialized.")

    async def setup(self) -> None:
        """Set up signal handlers for SIGINT and SIGTERM asynchronously.

        Raises:
            RuntimeError: If setup is called more than once.
        """
        if self._is_setup:
            msg = "SignalHandler.setup() has already been called."
            raise RuntimeError(msg)
        self._is_setup = True

        if sys.platform == "win32":
            # Set up signal handling directly in the main thread for Windows
            logger.debug("Setting up Windows signal handler.")
            signal.signal(signalnum=signal.SIGINT, handler=self._signal_handler)
            signal.signal(signalnum=signal.SIGTERM, handler=self._signal_handler)
        else:
            # For Unix-based systems, use asyncio signal handlers
            logger.debug("Setting up Unix signal handlers.")
            self.loop.add_signal_handler(
                signal.SIGINT,
                lambda: asyncio.create_task(self.handle_signal(signal.SIGINT)),
            )
            self.loop.add_signal_handler(
                signal.SIGTERM,
                lambda: asyncio.create_task(self.handle_signal(signal.SIGTERM)),
            )
            logger.debug("Signal handlers set up for SIGINT and SIGTERM.")
        await asyncio.sleep(0)  # Yield control to the event loop

    def _signal_handler(self, sig: int, _frame: types.FrameType | None) -> None:
        """Windows signal handling in the main thread."""
        logger.debug("Received shutdown signal: %s", signal.Signals(value=sig).name)
        if not self.stop_future.done():  # pragma: no branch
            asyncio.run_coroutine_threadsafe(coro=self._shutdown(), loop=self.loop)

    async def handle_signal(self, sig: signal.Signals) -> None:
        """Asynchronously handle the received signal.

        Args:
            sig (signal.Signals): The received signal.

        Raises:
            asyncio.CancelledError: If the shutdown is cancelled
        """
        logger.debug("Received shutdown signal: %s", sig.name)
        if not self.stop_future.done():
            await self._shutdown()

    async def _shutdown(self) -> None:
        """Shut down tasks and clean up gracefully."""
        logger.debug("Shutting down tasks and cleaning up.")
        if not self.stop_future.done():
            self.stop_future.set_result(None)
            await self._cancel_tasks()

    async def _cancel_tasks(self) -> None:
        """Cancel all running tasks except the current one."""
        current_task: asyncio.Task[object] | None = asyncio.current_task(self.loop)
        tasks: set[asyncio.Task[object]] = {
            task for task in asyncio.all_tasks(self.loop) if task is not current_task
        }

        if tasks:
            logger.debug("Cancelling %s running task(s)...", len(tasks))
            for task in tasks:
                task.cancel()

            await asyncio.wait(tasks, timeout=5.0)
            logger.debug("All tasks cancelled successfully.")
