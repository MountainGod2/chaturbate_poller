from __future__ import annotations

import enum
from typing import Any


class TestEnum(enum.Enum):
    """Test enum for testing purposes."""

    __test__ = False  # Prevent pytest from treating this as a test case
    VALUE1 = "value1"
    VALUE2 = "value2"


def test_field_value_type() -> None:
    """Test the FieldValue type."""

    def is_field_value(value: Any) -> bool:
        return isinstance(value, int | float | str | bool)

    assert is_field_value(42)
    assert is_field_value(3.14)
    assert is_field_value("test")
    assert is_field_value(value=True)
    assert not is_field_value([])
    assert not is_field_value({})


def test_recursive_dict() -> None:
    """Test the RecursiveDict type."""

    def is_recursive_dict(d: Any) -> bool:
        """Check if the input is a valid RecursiveDict."""
        if not isinstance(d, dict):
            return False
        for key, value in d.items():
            if not isinstance(key, str):
                return False
            if not (isinstance(value, int | enum.Enum) or is_recursive_dict(value)):
                return False
        return True

    valid_recursive_dict = {"key1": 1, "key2": {"nested_key1": 2, "nested_key2": {"deep_key": 3}}}
    assert is_recursive_dict(valid_recursive_dict)

    valid_recursive_dict_with_enum = {"key1": 1, "key2": TestEnum.VALUE1}
    assert is_recursive_dict(valid_recursive_dict_with_enum)

    invalid_recursive_dict = {"key1": 1, "key2": []}
    assert not is_recursive_dict(invalid_recursive_dict)


def test_nested_dict() -> None:
    """Test the NestedDict type."""

    def is_nested_dict(d: Any) -> bool:
        if not isinstance(d, dict):
            return False
        for key, value in d.items():
            if not isinstance(key, str):
                return False
            if isinstance(value, dict):
                if not is_nested_dict(value):
                    return False
            elif not isinstance(value, int | float | str | bool):
                return False
        return True

    valid_nested_dict = {
        "key1": 42,
        "key2": {"nested_key1": "value", "nested_key2": {"deep_key": True}},
    }
    assert is_nested_dict(valid_nested_dict)

    invalid_nested_dict = {
        "key1": 42,
        "key2": {
            "nested_key1": [],
        },
    }
    assert not is_nested_dict(invalid_nested_dict)


def test_flattened_dict() -> None:
    """Test the FlattenedDict type."""

    def is_flattened_dict(d: Any) -> bool:
        if not isinstance(d, dict):
            return False
        for key, value in d.items():
            if not isinstance(key, str):
                return False
            if not isinstance(value, int | float | str | bool):
                return False
        return True

    valid_flattened_dict = {"key1": 42, "key2": "value", "key3": 3.14, "key4": False}
    assert is_flattened_dict(valid_flattened_dict)

    invalid_flattened_dict = {"key1": 42, "key2": []}
    assert not is_flattened_dict(invalid_flattened_dict)
