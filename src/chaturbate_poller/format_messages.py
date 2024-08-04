"""Module to format different types of events from Chaturbate."""

from chaturbate_poller.models import Event


async def format_message(event: Event) -> str:
    """Handle different types of events from Chaturbate.

    Args:
        event (Event): The event object to handle.

    Returns:
        str: The formatted message.
    """
    if event.method in {"broadcastStart", "broadcastStop"}:
        message = format_broadcast_event(event)
    elif event.method in {"userEnter", "userLeave", "follow", "unfollow", "fanclubJoin"}:
        message = format_user_event(event)
    elif event.method in {"chatMessage", "privateMessage"}:
        message = format_message_event(event)
    elif event.method == "tip":
        message = format_tip_event(event)
    elif event.method == "roomSubjectChange":
        message = format_room_subject_change_event(event)
    elif event.method == "mediaPurchase":
        message = format_media_purchase_event(event)
    else:
        message = f"Unknown method: {event.method}"

    return message


def format_broadcast_event(event: Event) -> str:
    """Log broadcast events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    action = "started" if event.method == "broadcastStart" else "stopped"
    return f"Broadcast {action}"


def format_user_event(event: Event) -> str:
    """Log user events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    user = event.object.user.username if event.object.user else "Unknown user"
    if event.method == "userEnter":
        return f"{user} entered the room"
    if event.method == "userLeave":
        return f"{user} left the room"
    if event.method == "follow":
        return f"{user} followed"
    if event.method == "unfollow":
        return f"{user} unfollowed"
    if event.method == "fanclubJoin":
        return f"{user} joined the fanclub"
    return "Unknown user event"


def format_message_event(event: Event) -> str:
    """Log message events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    message = event.object.message
    if message:
        from_user = message.from_user
        content = message.message
        return f"{from_user} sent message: {content}"
    return "Unknown message event"


def format_tip_event(event: Event) -> str:
    """Log tip events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    if event.object.user and event.object.tip:
        user = event.object.user.username
        tokens = event.object.tip.tokens
        is_anon = "anonymously " if event.object.tip.is_anon else ""
        tip_message = (
            f"with message: '{event.object.tip.message}'" if event.object.tip.message else ""
        )
        return f"{user} tipped {is_anon}{tokens} tokens {tip_message}"
    return "Unknown tip event"


def format_room_subject_change_event(event: Event) -> str:
    """Log room subject change events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    subject = event.object.subject if event.object.subject else "unknown"
    return f"Room Subject changed to {subject}"


def format_media_purchase_event(event: Event) -> str:
    """Log media purchase events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    if event.object.user and event.object.media:
        user = event.object.user.username
        media_type = event.object.media.type.value
        media_name = event.object.media.name
        return f"{user} purchased {media_type} set: {media_name}"
    return "Unknown media purchase event"
