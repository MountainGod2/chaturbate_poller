"""Signal handler for SIGINT and SIGTERM signals."""

import asyncio
import logging
import signal
import sys

logger = logging.getLogger(__name__)


class SignalHandler:
    """Signal handler for SIGINT and SIGTERM signals."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        stop_future: asyncio.Future[None],
    ) -> None:
        """Initialize the SignalHandler.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop.
            stop_future (asyncio.Future[None]): The future to set when the signal is received.
        """
        self.loop = loop
        self.stop_future = stop_future
        logger.debug("SignalHandler initialized.")

    def setup(self) -> None:
        """Set up signal handlers for SIGINT and SIGTERM."""
        if sys.platform != "win32":
            self.loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
            self.loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)
            logger.debug("Signal handlers set up for SIGINT and SIGTERM.")
        else:
            logger.warning("Signal handlers not supported on this platform.")

    def handle_signal(self, sig: signal.Signals) -> None:
        """Handle the received signal.

        Args:
            sig (signal.Signals): The received signal.
        """
        logger.debug("Received signal %s. Initiating shutdown.", sig.name)
        if not self.stop_future.done():
            shutdown_task = self.loop.create_task(self._shutdown())
            self.loop.run_until_complete(shutdown_task)

    async def _shutdown(self) -> None:
        """Shut down tasks and clean up gracefully."""
        logger.debug("Shutting down tasks and cleaning up.")
        self.stop_future.set_result(None)
        await self._cancel_tasks()

    async def _cancel_tasks(self) -> None:
        """Cancel all running tasks except the current one."""
        current_task = asyncio.current_task()
        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not current_task]

        if tasks:
            logger.debug("Cancelling %d running task(s)...", len(tasks))
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        logger.debug("All tasks cancelled and cleaned up.")
