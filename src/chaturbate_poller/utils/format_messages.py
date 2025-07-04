"""Module to format different types of events from Chaturbate."""

from __future__ import annotations

import typing
from typing import Literal, LiteralString

from chaturbate_poller.constants import EventMethod

if typing.TYPE_CHECKING:
    from chaturbate_poller.models.event import Event
    from chaturbate_poller.models.media import Media
    from chaturbate_poller.models.message import Message
    from chaturbate_poller.models.tip import Tip


def format_message(event: Event) -> str | None:
    """Format a message for a given Chaturbate event."""
    # Map event methods to their formatters
    formatters = {
        EventMethod.BROADCAST_START.value: format_broadcast_event,
        EventMethod.BROADCAST_STOP.value: format_broadcast_event,
        EventMethod.USER_ENTER.value: format_user_event,
        EventMethod.USER_LEAVE.value: format_user_event,
        EventMethod.FOLLOW.value: format_user_event,
        EventMethod.UNFOLLOW.value: format_user_event,
        EventMethod.FANCLUB_JOIN.value: format_user_event,
        EventMethod.CHAT_MESSAGE.value: format_message_event,
        EventMethod.PRIVATE_MESSAGE.value: format_message_event,
        EventMethod.TIP.value: format_tip_event,
        EventMethod.ROOM_SUBJECT_CHANGE.value: format_room_subject_change_event,
        EventMethod.MEDIA_PURCHASE.value: format_media_purchase_event,
    }

    formatter = formatters.get(event.method)
    return formatter(event) if formatter else None


def format_broadcast_event(event: Event) -> str | None:
    """Format broadcast start/stop events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    action: typing.Literal["started", "stopped"] = (
        "started" if event.method == EventMethod.BROADCAST_START else "stopped"
    )
    return f"Broadcast {action}"


def format_user_event(event: Event) -> str | None:
    """Format user-related events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if not event.object.user:
        return None

    user: str = event.object.user.username
    messages: dict[str, str] = {
        EventMethod.USER_ENTER: f"{user} entered the room",
        EventMethod.USER_LEAVE: f"{user} left the room",
        EventMethod.FOLLOW: f"{user} followed",
        EventMethod.UNFOLLOW: f"{user} unfollowed",
        EventMethod.FANCLUB_JOIN: f"{user} joined the fanclub",
    }
    return messages.get(event.method)


def format_message_event(event: Event) -> str | None:
    """Format chat or private message events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if not event.object.message or not event.object.user:
        return None

    message: Message = event.object.message
    sender: str = event.object.user.username
    return f"{sender} sent message: {message.message}"


def format_tip_event(event: Event) -> str | None:
    """Format tip events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if not event.object.user or not event.object.tip:
        return None

    user: str = event.object.user.username
    tip: Tip = event.object.tip

    # Build message components
    anonymously: Literal["anonymously", ""] = "anonymously" if tip.is_anon else ""

    # Clean up message formatting
    tip_message = ""
    if tip.message:
        clean_message = tip.message.removeprefix(" | ").strip()
        if clean_message:
            tip_message = f" with message: '{clean_message}'"

    # Handle spacing properly for anonymous tips
    anon_part: LiteralString | Literal[""] = f" {anonymously}" if anonymously else ""
    return f"{user} tipped {tip.tokens} tokens{anon_part}{tip_message}"


def format_room_subject_change_event(event: Event) -> str | None:
    """Format room subject change events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    subject: str | None = event.object.subject
    return f"Room subject changed to: '{subject}'" if subject else None


def format_media_purchase_event(event: Event) -> str | None:
    """Format media purchase events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if not event.object.user or not event.object.media:
        return None

    user: str = event.object.user.username
    media: Media = event.object.media
    return f"{user} purchased {media.type} set: '{media.name}' for {media.tokens} tokens"
