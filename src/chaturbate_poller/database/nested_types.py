"""Utility module for defining types related to nested dictionaries."""

from __future__ import annotations

import enum
import typing

type FieldValue = float | int | str | bool

T = typing.TypeVar("T")
type RecursiveDict[T] = dict[str, T | dict[str, "RecursiveDict[T]"] | enum.Enum]

type NestedDict = RecursiveDict[FieldValue]

type FlattenedDict = dict[str, FieldValue]
