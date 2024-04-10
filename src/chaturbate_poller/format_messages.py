"""Module to format different types of events from Chaturbate."""

from chaturbate_poller.models import Event


async def format_message(event: Event) -> str:  # noqa: PLR0911
    """Handle different types of events from Chaturbate.

    Args:
        event (Event): The event object to handle.

    Returns:
        str: The formatted message.
    """
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
        case _:
            return str(f"Unknown method: {event.method}")
    return "Unknown method"


def format_broadcast_event(event: Event) -> str:
    """Log broadcast events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    action = "started" if event.method == "broadcastStart" else "stopped"
    return str(f"Broadcast {action}")


def format_user_event(event: Event) -> str:
    """Log user events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    user = event.object.user.username if event.object.user else "Unknown user"
    match event.method:
        case "userEnter":
            return f"{user} entered the room"
        case "userLeave":
            return f"{user} left the room"
        case "follow":
            return f"{user} followed"
        case "unfollow":
            return f"{user} unfollowed"
        case "fanclubJoin":
            return f"{user} joined the fanclub"
        case _:
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
        return str(f"{from_user} sent message: {content}")
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
        if event.object.tip.message:
            tip_message = f"with message: '{event.object.tip.message}'"
        else:
            tip_message = ""
        return str(f"{user} tipped {is_anon}{tokens} tokens {tip_message}")
    return "Unknown tip event"


def format_room_subject_change_event(event: Event) -> str:
    """Log room subject change events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    subject = event.object.subject if event.object.subject else "unknown"
    return str(f"Room Subject changed to {subject}")


def format_media_purchase_event(event: Event) -> str:
    """Log media purchase events.

    Args:
        event (Event): The event object to log.

    Returns:
        str: The formatted message.
    """
    if event.object.user and event.object.media:
        user = event.object.user.username
        # Use the .value attribute to get the string representation of the enum
        media_type = event.object.media.type.value
        media_name = event.object.media.name
        return str(f"{user} purchased {media_type} set: {media_name}")
    return "Unknown media purchase event"
