"""Tests for the logger module."""

import pytest


def test_logger_setup(caplog: pytest.LogCaptureFixture) -> None:
    """Test the logger setup."""
    from chaturbate_event_listener.logger import logger

    logger.setLevel("DEBUG")
    assert logger.name == "chaturbate_event_logger"
    assert logger.level == 10  # noqa: PLR2004

    with caplog.at_level(logger.level):
        logger.debug("Test debug message")
        assert "Test debug message" in caplog.text
        logger.info("Test info message")
        assert "Test info message" in caplog.text
        logger.warning("Test warning message")
        assert "Test warning message" in caplog.text
        logger.error("Test error message")
        assert "Test error message" in caplog.text
        logger.critical("Test critical message")
        assert "Test critical message" in caplog.text
