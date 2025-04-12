"""Utility module for defining types related to nested dictionaries."""

from __future__ import annotations

import enum
import typing

# FieldValue represents a value that can be int, float, str, or bool
type FieldValue = float | int | str | bool

T = typing.TypeVar("T")
# RecursiveDict[T] represents a dictionary with string keys and values that can be of type T, another RecursiveDict, or an enum.Enum  # noqa: E501
type RecursiveDict[T] = dict[str, T | dict[str, "RecursiveDict[T]"] | enum.Enum]

# NestedDict is a RecursiveDict where values are restricted to FieldValue
type NestedDict = RecursiveDict[FieldValue]

# FlattenedDict is a dictionary with string keys and FieldValue values
type FlattenedDict = dict[str, FieldValue]
