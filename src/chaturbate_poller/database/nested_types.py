"""Utility module for defining types related to nested dictionaries."""

from __future__ import annotations

import enum  # pragma: no cover
import typing  # pragma: no cover

# FieldValue represents a value that can be int, float, str, or bool
type FieldValue = float | int | str | bool  # pragma: no cover

T = typing.TypeVar("T")  # pragma: no cover
# RecursiveDict[T] represents a dictionary with string keys and values that can be of type T, another RecursiveDict, or an enum.Enum  # noqa: E501
type RecursiveDict[T] = dict[str, T | dict[str, "RecursiveDict[T]"] | enum.Enum]  # pragma: no cover

# NestedDict is a RecursiveDict where values are restricted to FieldValue
type NestedDict = RecursiveDict[FieldValue]  # pragma: no cover

# FlattenedDict is a dictionary with string keys and FieldValue values
type FlattenedDict = dict[str, FieldValue]  # pragma: no cover
