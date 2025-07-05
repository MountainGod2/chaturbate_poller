"""Polling logic for Chaturbate events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chaturbate_poller.core.client import ChaturbateClient

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from chaturbate_poller.config.backoff import BackoffConfig
    from chaturbate_poller.handlers.event_handler import EventHandler
    from chaturbate_poller.models.event import Event


async def poll_events(client: ChaturbateClient) -> AsyncIterator[Event]:
    """Poll for events continuously, yielding each event.

    Args:
        client: Configured Chaturbate client instance.

    Yields:
        Individual events from the API response.
    """
    next_url: str | None = None
    while response := await client.fetch_events(url=next_url):
        for event in response.events:
            yield event
        if not (next_url := response.next_url):
            break


async def start_polling(  # noqa: PLR0913
    username: str,
    token: str,
    api_timeout: int,
    event_handler: EventHandler,
    *,
    testbed: bool = False,
    backoff_config: BackoffConfig | None = None,
) -> None:
    """Start polling Chaturbate events with configured handler.

    Args:
        username: Chaturbate username.
        token: Chaturbate API token.
        api_timeout: Request timeout in seconds.
        event_handler: Handler for processing events.
        testbed: Use testbed environment.
        backoff_config: Retry configuration.
    """
    async with ChaturbateClient(
        username=username,
        token=token,
        timeout=api_timeout,
        testbed=testbed,
        backoff_config=backoff_config,
    ) as client:
        async for event in poll_events(client):
            await event_handler.handle_event(event)
