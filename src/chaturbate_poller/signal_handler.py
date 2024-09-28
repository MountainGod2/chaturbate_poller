"""Signal handler for SIGINT and SIGTERM signals."""

import asyncio
import logging
import signal
import sys


class SignalHandler:
    """Signal handler for SIGINT and SIGTERM signals."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stop_future: asyncio.Future[None],
    ) -> None:
        """Signal handler for SIGINT and SIGTERM signals.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): The future to set when the signal is received.

        Attributes:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): The future to set when the signal is received.
            logger (logging.Logger): The logger instance.
        """
        self.logger = logging.getLogger(__name__)
        self.loop = loop
        self.stop_future = stop_future
        self.logger.debug("SignalHandler initialized.")

    def setup(self) -> None:
        """Set up signal handlers for SIGINT and SIGTERM."""
        if sys.platform != "win32":
            self.loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
            self.loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)
            self.logger.debug("Signal handlers set up for SIGINT and SIGTERM.")
        else:
            self.logger.warning("Signal handlers not supported on this platform.")

    def handle_signal(self, sig: signal.Signals) -> None:
        """Handle the signal received.

        Args:
            sig (signal.Signals): The signal received.
        """
        self.logger.debug("Received signal %s. Initiating shutdown.", sig.name)
        if not self.stop_future.done():
            self.loop.create_task(self._shutdown())

    async def _shutdown(self) -> None:
        """Shut down the tasks and clean up."""
        self.logger.debug("Shutting down tasks and cleaning up.")
        self.stop_future.set_result(None)
        await self._cancel_tasks()

    async def _cancel_tasks(self) -> None:
        """Cancel all tasks except the current task and clean up."""
        current_task = asyncio.current_task()
        tasks = [task for task in asyncio.all_tasks() if task is not current_task]

        if tasks:
            for task in tasks:
                task.cancel()

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                    self.logger.error("Exception during task cancellation: %s", result)
        self.logger.debug("All tasks cancelled and cleaned up.")
