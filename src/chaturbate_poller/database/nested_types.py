"""Utility module for defining types related to nested dictionaries."""

from enum import Enum
from typing import TypeVar

type FieldValue = float | int | str | bool

T = TypeVar("T")
type RecursiveDict[T] = dict[str, T | dict[str, "RecursiveDict[T]"] | Enum]

type NestedDict = RecursiveDict[FieldValue]

type FlattenedDict = dict[str, FieldValue]
