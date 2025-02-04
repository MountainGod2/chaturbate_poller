import json
import logging
from typing import Any

from _typeshed import Incomplete

BUILTIN_ATTRS: Incomplete

class JSONFormatter(logging.Formatter):
    json_lib = json
    def format(self, record: logging.LogRecord) -> str: ...
    def to_json(self, record: logging.LogRecord) -> dict[str, Any]: ...
    def extra_from_record(self, record: logging.LogRecord) -> dict[str, Any]: ...
    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]: ...
    def mutate_json_record(
        self, json_record: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]: ...

class VerboseJSONFormatter(JSONFormatter):
    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]: ...

class FlatJSONFormatter(JSONFormatter):
    keep: Incomplete
    def json_record(
        self, message: str, extra: dict[str, Any], record: logging.LogRecord
    ) -> dict[str, Any]: ...
