import pytest

from chaturbate_poller.format_messages import (
    format_media_purchase_event,
    format_message,
    format_message_event,
    format_tip_event,
)
from chaturbate_poller.models import (
    Event,
    EventData,
    Gender,
    Tip,
    User,
)


class TestFormatMessages:
    """Tests for message formatting."""

    @pytest.mark.asyncio
    async def test_format_message_tip_with_message(self) -> None:
        """Test formatting a tip with a message."""
        message = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="example message", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "example_user tipped 100 tokens with message: 'example message'"

    @pytest.mark.asyncio
    async def test_format_message_tip_without_message(self) -> None:
        """Test formatting a tip without a message."""
        message = await format_message(
            Event(
                method="tip",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=User(
                        username="example_user",
                        inFanclub=False,
                        gender=Gender.MALE,
                        hasTokens=True,
                        recentTips="none",
                        isMod=False,
                    ),
                    tip=Tip(tokens=100, message="", isAnon=False),
                ),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "example_user tipped 100 tokens "

    def test_format_tip_event_unknown_tip_event(self) -> None:
        """Test formatting a tip event with an unknown tip event."""
        message = format_tip_event(
            Event(
                method="tip",
                object=EventData(broadcaster="example_broadcaster", user=None, tip=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown tip event"

    def test_format_message_event_unknown_message_event(self) -> None:
        """Test formatting a message event with an unknown message event."""
        message = format_message_event(
            Event(
                method="unknown",
                object=EventData(broadcaster="example_broadcaster", user=None, tip=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown message event"

    def test_format_media_purchase_event_unknown_media_purchase_event(self) -> None:
        """Test formatting a media purchase event with an unknown media purchase event."""
        message = format_media_purchase_event(
            Event(
                method="mediaPurchase",
                object=EventData(broadcaster="example_broadcaster", user=None, media=None),
                id="UNIQUE_EVENT_ID",
            )
        )
        assert message == "Unknown media purchase event"
