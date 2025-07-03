"""Tests for backoff configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from chaturbate_poller.config.backoff import BackoffConfig, backoff_config

if TYPE_CHECKING:
    from collections.abc import Generator


class TestBackoffConfig:
    """Tests for BackoffConfig class."""

    def test_singleton_pattern(self) -> None:
        """Test that the global backoff_config instance is available."""
        # Just verify the global instance exists and works
        assert backoff_config.enabled is True
        assert isinstance(backoff_config.max_tries, int)

        # Each BackoffConfig() call creates a new instance
        config1 = BackoffConfig()
        config2 = BackoffConfig()
        assert config1 is not config2

    def test_default_initialization(self) -> None:
        """Test default initialization values."""
        config = BackoffConfig()

        assert config.enabled is True
        assert config.max_tries == 6  # MAX_RETRIES
        assert config.base == 2.0  # BACKOFF_BASE
        assert config.factor == 2.0  # BACKOFF_FACTOR
        assert config.constant_interval == 10  # CONSTANT_INTERVAL
        assert config.read_error_max_tries == 5  # READ_ERROR_MAX_TRIES

    def test_disable_for_tests(self) -> None:
        """Test disabling backoff for tests."""
        config = BackoffConfig()

        config.disable_for_tests()

        assert config.enabled is False
        # When disabled, get_max_tries returns 1
        assert config.get_max_tries() == 1
        assert config.get_read_error_max_tries() == 1

    def test_enable(self) -> None:
        """Test enabling backoff behavior."""
        config = BackoffConfig()

        # First disable it
        config.disable_for_tests()
        assert config.enabled is False

        # Then enable it
        config.enable()

        assert config.enabled is True
        assert config.max_tries == 6  # MAX_RETRIES
        assert config.read_error_max_tries == 5  # READ_ERROR_MAX_TRIES

    def test_get_max_tries(self) -> None:
        """Test get_max_tries method."""
        config = BackoffConfig()

        # Test with enabled state
        config.enable()
        assert config.get_max_tries() == 6

        # Test with disabled state
        config.disable_for_tests()
        assert config.get_max_tries() == 1

    def test_get_read_error_max_tries(self) -> None:
        """Test get_read_error_max_tries method."""
        config = BackoffConfig()

        # Test with enabled state
        config.enable()
        assert config.get_read_error_max_tries() == 5  # READ_ERROR_MAX_TRIES

        # Test with disabled state
        config.disable_for_tests()
        assert config.get_read_error_max_tries() == 1

    def test_get_base_when_enabled(self) -> None:
        """Test get_base method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_base() == 2.0  # BACKOFF_BASE

    def test_get_base_when_disabled(self) -> None:
        """Test get_base method when backoff is disabled."""
        config = BackoffConfig()
        config.disable_for_tests()

        assert config.get_base() == 1

    def test_get_factor_when_enabled(self) -> None:
        """Test get_factor method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_factor() == 2.0  # BACKOFF_FACTOR

    def test_get_factor_when_disabled(self) -> None:
        """Test get_factor method when backoff is disabled."""
        config = BackoffConfig()
        config.disable_for_tests()

        assert config.get_factor() == 0

    def test_get_constant_interval_when_enabled(self) -> None:
        """Test get_constant_interval method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_constant_interval() == 10  # CONSTANT_INTERVAL

    def test_get_constant_interval_when_disabled(self) -> None:
        """Test get_constant_interval method when backoff is disabled."""
        config = BackoffConfig()
        config.disable_for_tests()

        assert config.get_constant_interval() == 0

    def test_state_persistence_across_operations(self) -> None:
        """Test that state changes persist across multiple operations."""
        config = BackoffConfig()

        # Start with enabled state
        config.enable()
        assert config.enabled is True
        assert config.get_base() == 2.0  # BACKOFF_BASE
        assert config.get_factor() == 2.0  # BACKOFF_FACTOR
        assert config.get_constant_interval() == 10  # CONSTANT_INTERVAL

        # Disable and verify all getters reflect disabled state
        config.disable_for_tests()
        assert config.enabled is False
        assert config.get_base() == 1
        assert config.get_factor() == 0
        assert config.get_constant_interval() == 0

        # Re-enable and verify restoration
        config.enable()
        assert config.enabled is True
        assert config.get_base() == 2.0  # BACKOFF_BASE
        assert config.get_factor() == 2.0  # BACKOFF_FACTOR
        assert config.get_constant_interval() == 10  # CONSTANT_INTERVAL

    def test_initialization_idempotence(self) -> None:
        """Test that each BackoffConfig instance has proper default initialization."""
        config = BackoffConfig()

        # Modify the configuration
        config.disable_for_tests()

        # Create a new instance - should have default values
        new_config = BackoffConfig()

        # New instance should have default values, not the modified values
        assert new_config.enabled is True  # Default enabled state
        assert new_config.max_tries == 6  # Default MAX_RETRIES
        assert new_config is not config  # Different instances

    @pytest.fixture(autouse=True)
    def restore_config_state(self) -> Generator[None]:
        """Restore config to default state before and after each test."""
        # Reset global backoff_config to default state before each test
        backoff_config.enabled = True
        backoff_config.max_tries = 6
        backoff_config.read_error_max_tries = 5
        backoff_config.base = 2.0
        backoff_config.factor = 2.0
        backoff_config.constant_interval = 10

        yield

        # Reset again after each test
        backoff_config.enabled = True
        backoff_config.max_tries = 6
        backoff_config.read_error_max_tries = 5
        backoff_config.base = 2.0
        backoff_config.factor = 2.0
        backoff_config.constant_interval = 10
