"""Tests for the logger module."""


def test_logger_basic() -> None:
    """Basic test to ensure logger is configured."""
    from chaturbate_event_listener.logger import logger

    assert logger is not None
    assert logger.name == "chaturbate_event_listener"
    assert len(logger.handlers) == 2  # noqa: PLR2004
