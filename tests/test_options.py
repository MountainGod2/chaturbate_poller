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

    def test_float_timeout_accepted(self) -> None:
        """Test that float timeout is accepted due to lack of runtime type checking.

        Note: The current dataclass implementation doesn't enforce runtime type validation.
        Float values are accepted and stored as-is.
        """
        options = PollerOptions(
            username="test_user",
            token="test_token",  # noqa: S106
            timeout=30.5,  # type: ignore[arg-type]
        )
        assert options.timeout == 30.5

    def test_none_timeout_causes_validation_error(self) -> None:
        """Test that None timeout causes error during validation.

        The __post_init__ method tries to compare timeout < 0, which will fail with None.
        """
        with pytest.raises(TypeError):
            PollerOptions(
                username="test_user",
                token="test_token",  # noqa: S106
                timeout=None,  # type: ignore[arg-type]
            )

    def test_list_timeout_causes_validation_error(self) -> None:
        """Test that list timeout causes error during validation.

        The __post_init__ method tries to compare timeout < 0, which will fail with a list.
        """
        with pytest.raises(TypeError):
            PollerOptions(
                username="test_user",
                token="test_token",  # noqa: S106
                timeout=[30],  # type: ignore[arg-type]
            )

    def test_type_validation_comprehensive(self) -> None:
        """Test comprehensive type validation behavior.

        This test demonstrates how different wrong types interact with validation logic
        and documents the current behavior of the dataclass implementation.
        """
        # String timeout causes TypeError during validation
        with pytest.raises(
            TypeError, match="'<' not supported between instances of 'str' and 'int'"
        ):
            PollerOptions(
                username="test_user",
                token="test_token",  # noqa: S106
                timeout="abc",  # type: ignore[arg-type]
            )

        # None values cause validation failure due to empty check for username/token
        with pytest.raises(ValueError, match="Username and token are required."):
            PollerOptions(
                username=None,  # type: ignore[arg-type]
                token="test_token",  # noqa: S106
                timeout=0,
            )

        # Numeric types that aren't strings work fine for username/token
        # Float timeout is accepted, non-bool values are accepted for boolean fields
        options = PollerOptions(
            username=123,  # type: ignore[arg-type]
            token=456,  # type: ignore[arg-type]
            timeout=30.5,  # type: ignore[arg-type]
            testbed="true",  # type: ignore[arg-type]
            use_database=1,  # type: ignore[arg-type]
            verbose=0,  # type: ignore[arg-type]
        )
        assert options.username == 123  # type: ignore[comparison-overlap]
        assert options.token == 456  # type: ignore[comparison-overlap]
        assert options.timeout == 30.5
        assert options.testbed == "true"  # type: ignore[comparison-overlap]
        assert options.use_database == 1
        assert options.verbose == 0
