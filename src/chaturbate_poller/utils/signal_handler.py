"""Signal handler for SIGINT and SIGTERM signals."""

import asyncio
import logging
import signal
from typing import Any

logger = logging.getLogger(__name__)
"""logging.Logger: The module-level logger."""


class SignalHandler:
    """Signal handler for SIGINT and SIGTERM signals."""

    def __init__(self, loop: asyncio.AbstractEventLoop, stop_future: asyncio.Future[None]) -> None:
        """Initialize the SignalHandler.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): The future to set when the signal is received.
        """
        self.loop = loop
        self.stop_future = stop_future
        self._is_setup = False
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

        self.loop.add_signal_handler(
            signal.SIGINT, lambda: asyncio.create_task(self.handle_signal(signal.SIGINT))
        )
        self.loop.add_signal_handler(
            signal.SIGTERM, lambda: asyncio.create_task(self.handle_signal(signal.SIGTERM))
        )
        logger.debug("Signal handlers set up for SIGINT and SIGTERM.")

    async def handle_signal(self, sig: signal.Signals) -> None:
        """Asynchronously handle the received signal.

        Args:
            sig (signal.Signals): The received signal.
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
        """Cancel all running tasks except the current one.

        Logs any exceptions during cancellation and enforces a timeout.
        """
        current_task = asyncio.current_task()
        tasks: list[asyncio.Task[Any]] = [
            task for task in asyncio.all_tasks(self.loop) if task is not current_task
        ]

        if tasks:
            logger.debug("Cancelling %s running task(s)...", len(tasks))
            for task in tasks:
                task.cancel()

            await asyncio.wait(tasks, timeout=5.0)
            logger.debug("All tasks cancelled successfully.")
