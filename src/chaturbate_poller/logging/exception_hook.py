"""Uncaught exception handler for fatal errors."""

import logging
import sys
import types

logger = logging.getLogger(__name__)


def handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: types.TracebackType | None,
) -> None:
    """Handle uncaught exceptions with logging and clean exit.

    Args:
        exc_type: The exception type.
        exc_value: The exception instance.
        exc_traceback: The traceback object.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow Ctrl+C to exit silently
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception, application will terminate.")
    sys.exit(1)
