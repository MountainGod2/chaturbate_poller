"""This module contains data classes for the Chaturbate Event Listener."""

from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class User(DataClassJsonMixin):
    """A data class representing a user."""

    username: str
    in_fanclub: bool
    has_tokens: bool
    is_mod: bool
    recent_tips: str
    gender: str
    subgender: str
    color_group: str | None = None
    fc_auto_renew: bool | None = None
    has_darkmode: bool | None = None
    in_private_show: bool | None = None
    is_broadcasting: bool | None = None
    is_follower: bool | None = None
    is_owner: bool | None = None
    is_silenced: bool | None = None
    is_spying: bool | None = None
    language: str | None = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Media(DataClassJsonMixin):
    """A data class representing media."""

    id: int
    type: str
    name: str
    tokens: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Message(DataClassJsonMixin):
    """A data class representing a message."""

    color: str
    font: str
    message: str
    bg_color: str | None = None
    to_user: str | None = None
    from_user: str | None = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Tip(DataClassJsonMixin):
    """A data class representing a tip."""

    is_anon: bool
    message: str
    tokens: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EventObject(DataClassJsonMixin):
    """A data class representing an event object."""

    broadcaster: str
    subject: str | None = None
    media: Media | None = None
    message: Message | None = None
    tip: Tip | None = None
    user: User | None = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Event(DataClassJsonMixin):
    """A data class representing an event."""

    method: str
    id: str
    object: EventObject
