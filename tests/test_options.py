"""Tests for PollerOptions model."""

import pytest

from chaturbate_poller.models.options import PollerOptions


class TestPollerOptions:
    """Tests for the PollerOptions model."""

    def test_valid_options(self) -> None:
        """Test creating PollerOptions with valid parameters."""
        options = PollerOptions(
            username="test_user",
            token="test_token",  # noqa: S106
            timeout=30,
            testbed=True,
            use_database=True,
            verbose=True,
        )
        assert options.username == "test_user"
        assert options.token == "test_token"  # noqa: S105
        assert options.timeout == 30
        assert options.testbed is True
        assert options.use_database is True
        assert options.verbose is True

    def test_empty_username_raises_error(self) -> None:
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Username and token are required."):
            PollerOptions(
                username="",
                token="test_token",  # noqa: S106
                timeout=30,
            )

    def test_empty_token_raises_error(self) -> None:
        """Test that empty token raises ValueError."""
        with pytest.raises(ValueError, match="Username and token are required."):
            PollerOptions(
                username="test_user",
                token="",
                timeout=30,
            )

    def test_both_empty_raises_error(self) -> None:
        """Test that both empty username and token raise ValueError."""
        with pytest.raises(ValueError, match="Username and token are required."):
            PollerOptions(
                username="",
                token="",
                timeout=30,
            )

    def test_negative_timeout_raises_error(self) -> None:
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be a non-negative integer."):
            PollerOptions(
                username="test_user",
                token="test_token",  # noqa: S106
                timeout=-1,
            )

    def test_zero_timeout_valid(self) -> None:
        """Test that zero timeout is valid."""
        options = PollerOptions(
            username="test_user",
            token="test_token",  # noqa: S106
            timeout=0,
        )
        assert options.timeout == 0

    def test_default_values(self) -> None:
        """Test default values for optional parameters."""
        options = PollerOptions(
            username="test_user",
            token="test_token",  # noqa: S106
            timeout=30,
        )
        assert options.testbed is False
        assert options.use_database is False
        assert options.verbose is False
