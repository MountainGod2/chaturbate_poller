"""Module to format different types of events from Chaturbate."""

from chaturbate_poller.models.event import Event


def format_message(event: Event) -> str | None:  # noqa: PLR0911  # pylint: disable=too-many-return-statements
    """Format a message for a given Chaturbate event."""
    match event.method:
        case "broadcastStart" | "broadcastStop":
            return format_broadcast_event(event)
        case "userEnter" | "userLeave" | "follow" | "unfollow" | "fanclubJoin":
            return format_user_event(event)
        case "chatMessage" | "privateMessage":
            return format_message_event(event)
        case "tip":
            return format_tip_event(event)
        case "roomSubjectChange":
            return format_room_subject_change_event(event)
        case "mediaPurchase":
            return format_media_purchase_event(event)
        case _:  # pragma: no cover
            return None


def format_broadcast_event(event: Event) -> str | None:
    """Format broadcast start/stop events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if event.method in {"broadcastStart", "broadcastStop"}:
        action = "started" if event.method == "broadcastStart" else "stopped"
        return f"Broadcast {action}"
    return None  # pragma: no cover


def format_user_event(event: Event) -> str | None:
    """Format user-related events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if event.object.user:
        user = event.object.user.username
        messages = {
            "userEnter": f"{user} entered the room",
            "userLeave": f"{user} left the room",
            "follow": f"{user} followed",
            "unfollow": f"{user} unfollowed",
            "fanclubJoin": f"{user} joined the fanclub",
        }
        return messages.get(event.method, None)
    return None


def format_message_event(event: Event) -> str | None:
    """Format chat or private message events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    message = event.object.message
    if message and event.object.user:
        sender = event.object.user.username
        return f"{sender} sent message: {message.message}"
    return None  # pragma: no cover


def format_tip_event(event: Event) -> str | None:
    """Format tip events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    user = event.object.user.username if event.object.user else None
    tip = event.object.tip
    if tip:
        is_anon = "anonymously " if tip.is_anon else ""
        tip_message = f"with message: '{tip.message.removeprefix(' | ')}'" if tip.message else ""
        return f"{user} tipped {tip.tokens} tokens {is_anon}{tip_message}".strip()
    return None


def format_room_subject_change_event(event: Event) -> str | None:
    """Format room subject change events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    subject = event.object.subject or None
    return f"Room subject changed to: '{subject}'" if subject else None


def format_media_purchase_event(event: Event) -> str | None:
    """Format media purchase events.

    Args:
        event (Event): The event object to format.

    Returns:
        str | None: The formatted message or None if unrecognized.
    """
    if event.object.user:
        user = event.object.user.username
        media = event.object.media
        if media:
            return f"{user} purchased {media.type} set: '{media.name}' for {media.tokens} tokens"
    return None  # pragma: no cover
