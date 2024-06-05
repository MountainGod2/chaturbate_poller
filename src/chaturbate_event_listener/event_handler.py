# src/chaturbate_event_listener/event_handler.py
"""Default event handler function for the package."""

import re
from collections.abc import Callable
from typing import Any

from chaturbate_event_listener.logger import logger
from chaturbate_event_listener.utils import get_username, log_incomplete_event


class EventHandler:
    """Event handler class for the chaturbate_event_listener package.

    This class handles the different event types received from the Chaturbate API and
    calls the appropriate event callback function.

    Args:
        event_callback (Callable[[dict[str, Any]], None], optional): The event callback
            function. Defaults to None.
    """

    def __init__(
        self, event_callback: Callable[[dict[str, Any]], None] | None = None
    ) -> None:
        """Initialize the EventHandler class."""
        self.event_callback = event_callback or self.default_event_callback

    def __call__(self, message: dict[str, Any]) -> None:
        """Call the event callback function.

        Args:
            message (dict[str, Any]): The event message.
        """
        self.event_callback(message)

    def default_event_callback(self, message: dict[str, Any]) -> None:
        """Default event callback function.

        Args:
            message (dict[str, Any]): The event message.
        """
        method = message.get("method")

        if method:
            method = re.sub(r"(?<!^)(?=[A-Z])", "_", method).lower()
            handler_method = getattr(
                self, f"handle_{method.lower()}", self.unknown_method
            )
            handler_method(message)
        else:
            logger.warning("Unknown method: %s", method)

    def handle_broadcast_start(self, message: dict[str, Any]) -> None:
        """Handle 'broadcastStart' event."""
        broadcaster = message.get("object", {}).get("broadcaster", {}).get("username")
        if broadcaster:
            logger.info("Broadcast started by %s", broadcaster)
        else:
            self.incomplete_event(message)

    def handle_broadcast_stop(self, message: dict[str, Any]) -> None:
        """Handle 'broadcastStop' event."""
        broadcaster = message.get("object", {}).get("broadcaster", {}).get("username")
        if broadcaster:
            logger.info("Broadcast stopped by %s", broadcaster)
        else:
            self.incomplete_event(message)

    def handle_user_enter(self, message: dict[str, Any]) -> None:
        """Handle 'userEnter' event."""
        user = get_username(message)
        if user:
            logger.info("%s entered the room", user)
        else:
            self.incomplete_event(message)

    def handle_user_leave(self, message: dict[str, Any]) -> None:
        """Handle 'userLeave' event."""
        user = get_username(message)
        if user:
            logger.info("%s left the room", user)
        else:
            self.incomplete_event(message)

    def handle_follow(self, message: dict[str, Any]) -> None:
        """Handle 'follow' event."""
        user = get_username(message)
        if user:
            logger.info("%s has followed", user)
        else:
            self.incomplete_event(message)

    def handle_unfollow(self, message: dict[str, Any]) -> None:
        """Handle 'unfollow' event."""
        user = get_username(message)
        if user:
            logger.info("%s has unfollowed", user)
        else:
            self.incomplete_event(message)

    def handle_fanclub_join(self, message: dict[str, Any]) -> None:
        """Handle 'fanclubJoin' event."""
        user = get_username(message)
        if user:
            logger.info("%s joined the fan club", user)
        else:
            self.incomplete_event(message)

    def handle_chat_message(self, message: dict[str, Any]) -> None:
        """Handle 'chatMessage' event."""
        user = get_username(message)
        chat_message = message.get("object", {}).get("message", {}).get("message")
        if user and chat_message:
            logger.info("%s sent chat message: %s", user, chat_message)
        else:
            self.incomplete_event(message)

    def handle_private_message(self, message: dict[str, Any]) -> None:
        """Handle 'privateMessage' event."""
        from_user = message.get("object", {}).get("message", {}).get("fromUser")
        to_user = message.get("object", {}).get("message", {}).get("toUser")
        private_message = message.get("object", {}).get("message", {}).get("message")
        if from_user and to_user and private_message:
            logger.info(
                "%s sent private message to %s: %s", from_user, to_user, private_message
            )
        else:
            self.incomplete_event(message)

    def handle_tip(self, message: dict[str, Any]) -> None:
        """Handle 'tip' event."""
        user = get_username(message)
        tokens = message.get("object", {}).get("tip", {}).get("tokens")
        is_anon = (
            "anonymously"
            if message.get("object", {}).get("tip", {}).get("isAnon")
            else ""
        )
        tip_message = (
            message.get("object", {}).get("tip", {}).get("message", "").strip()
        )

        if tip_message.startswith("|"):
            tip_message = tip_message[1:].strip()
        if tip_message:
            tip_message = f"with message: {tip_message}"

        if user and tokens:
            log_message_parts = [f"{user} tipped {tokens} tokens"]
            if is_anon:
                log_message_parts.append(is_anon)
            if tip_message:
                log_message_parts.append(tip_message)

            log_message = " ".join(log_message_parts)
            logger.info(log_message)
        else:
            self.incomplete_event(message)

    def handle_room_subject_change(self, message: dict[str, Any]) -> None:
        """Handle 'roomSubjectChange' event."""
        subject = message.get("object", {}).get("subject")
        if subject:
            logger.info("Room subject changed to: %s", subject)
        else:
            self.incomplete_event(message)

    def handle_media_purchase(self, message: dict[str, Any]) -> None:
        """Handle 'mediaPurchase' event."""
        user = get_username(message)
        media_type = message.get("object", {}).get("media", {}).get("type")
        media_name = message.get("object", {}).get("media", {}).get("name")
        if user and media_type and media_name:
            logger.info("%s purchased %s set: %s", user, media_type, media_name)
        else:
            self.incomplete_event(message)

    def incomplete_event(self, message: dict[str, Any]) -> None:
        """Log an incomplete event."""
        log_incomplete_event(self.__class__.__name__, message)

    def unknown_method(self, message: dict[str, Any]) -> None:
        """Handle unknown event method."""
        logger.warning("Unknown method: %s", message.get("method"))
