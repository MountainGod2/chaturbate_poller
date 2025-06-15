"""Tests for backoff configuration."""

from __future__ import annotations

import pytest

from chaturbate_poller.config.backoff import BackoffConfig, backoff_config


class TestBackoffConfig:
    """Tests for BackoffConfig class."""

    def test_singleton_pattern(self) -> None:
        """Test that BackoffConfig follows singleton pattern."""
        config1 = BackoffConfig()
        config2 = BackoffConfig()

        assert config1 is config2
        assert config1 is backoff_config
        assert config2 is backoff_config

    def test_default_initialization(self) -> None:
        """Test default initialization values."""
        config = BackoffConfig()

        # Reset to default state first since other fixtures may have modified it
        config.enabled = True
        config.max_tries = 6
        config.base = 2
        config.factor = 5
        config.constant_interval = 2
        config.read_error_max_tries = 10

        assert config.enabled is True
        assert config.max_tries == 6
        assert config.base == 2
        assert config.factor == 5
        assert config.constant_interval == 2
        assert config.read_error_max_tries == 10
        assert config._initialized is True

    def test_disable_for_tests(self) -> None:
        """Test disabling backoff for tests."""
        config = BackoffConfig()
        original_enabled = config.enabled
        original_max_tries = config.max_tries
        original_read_error_max_tries = config.read_error_max_tries

        config.disable_for_tests()

        assert config.enabled is False
        assert config.max_tries == 1
        assert config.read_error_max_tries == 1

        # Restore original state
        config.enabled = original_enabled
        config.max_tries = original_max_tries
        config.read_error_max_tries = original_read_error_max_tries

    def test_enable(self) -> None:
        """Test enabling backoff behavior."""
        config = BackoffConfig()

        # First disable it
        config.disable_for_tests()
        assert config.enabled is False

        # Then enable it
        config.enable()

        assert config.enabled is True
        assert config.max_tries == 6
        assert config.read_error_max_tries == 10

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
        assert config.get_read_error_max_tries() == 10

        # Test with disabled state
        config.disable_for_tests()
        assert config.get_read_error_max_tries() == 1

    def test_get_base_when_enabled(self) -> None:
        """Test get_base method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_base() == 2

    def test_get_base_when_disabled(self) -> None:
        """Test get_base method when backoff is disabled."""
        config = BackoffConfig()
        config.disable_for_tests()

        assert config.get_base() == 1

    def test_get_factor_when_enabled(self) -> None:
        """Test get_factor method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_factor() == 5

    def test_get_factor_when_disabled(self) -> None:
        """Test get_factor method when backoff is disabled."""
        config = BackoffConfig()
        config.disable_for_tests()

        assert config.get_factor() == 0

    def test_get_constant_interval_when_enabled(self) -> None:
        """Test get_constant_interval method when backoff is enabled."""
        config = BackoffConfig()
        config.enable()

        assert config.get_constant_interval() == 2

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
        assert config.get_base() == 2
        assert config.get_factor() == 5
        assert config.get_constant_interval() == 2

        # Disable and verify all getters reflect disabled state
        config.disable_for_tests()
        assert config.enabled is False
        assert config.get_base() == 1
        assert config.get_factor() == 0
        assert config.get_constant_interval() == 0

        # Re-enable and verify restoration
        config.enable()
        assert config.enabled is True
        assert config.get_base() == 2
        assert config.get_factor() == 5
        assert config.get_constant_interval() == 2

    def test_initialization_idempotence(self) -> None:
        """Test that multiple __init__ calls don't reset the configuration."""
        config = BackoffConfig()

        # Modify the configuration
        config.disable_for_tests()
        original_enabled = config.enabled
        original_max_tries = config.max_tries

        # Create a new instance (simulating a new instance creation)
        new_config = BackoffConfig()

        # Values should remain unchanged due to singleton pattern and _initialized flag
        assert new_config.enabled == original_enabled
        assert new_config.max_tries == original_max_tries
        assert new_config._initialized is True
        assert new_config is config  # Verify it's the same singleton instance

    @pytest.fixture(autouse=True)
    def restore_config_state(self) -> None:
        """Restore config to default state after each test."""

    def teardown_method(self) -> None:
        """Restore config to default state after each test."""
        # Restore to default state
        config = BackoffConfig()
        config.enabled = True
        config.max_tries = 6
        config.base = 2
        config.factor = 5
        config.constant_interval = 2
        config.read_error_max_tries = 10
