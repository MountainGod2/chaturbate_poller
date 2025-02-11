"""Polling logic for Chaturbate events."""

from collections.abc import AsyncIterator

from chaturbate_poller.core.client import ChaturbateClient
from chaturbate_poller.handlers.event_handler import EventHandler
from chaturbate_poller.models.event import Event


async def poll_events(client: ChaturbateClient) -> AsyncIterator[Event]:
    """Continuously fetch events, yielding each event individually."""
    next_url: str | None = None
    while response := await client.fetch_events(next_url):
        for event in response.events:
            yield event
        if not (next_url := response.next_url):
            break


async def start_polling(
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool = False,
) -> None:
    """Begin polling Chaturbate events and handle them.

    Args:
        username (str): The Chaturbate username.
        token (str): The Chaturbate token.
        api_timeout (int): Timeout for API requests in seconds.
        event_handler (EventHandler): The event handler to process events.
        testbed (bool, optional): Whether to use the testbed environment. Defaults to False.
    """
    async with ChaturbateClient(
        username=username, token=token, timeout=api_timeout, testbed=testbed
    ) as client:
        async for event in poll_events(client):
            await event_handler.handle_event(event)
