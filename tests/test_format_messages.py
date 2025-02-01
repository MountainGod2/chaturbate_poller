import pytest

from chaturbate_poller.format_messages import format_message
from chaturbate_poller.models import Event, EventData, Media, Message, Tip, User


class TestFormatMessages:
    """Tests for formatting event messages."""

    @pytest.mark.asyncio
    async def test_format_tip_with_message(self, example_user: User) -> None:
        """Test formatting of a tip event message."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message=" | example message", isAnon=False),
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user tipped 100 tokens with message: 'example message'"

    @pytest.mark.asyncio
    async def test_format_tip_with_message_no_prefix(self, example_user: User) -> None:
        """Test formatting of a tip event message without the prefix."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message="example message", isAnon=False),
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user tipped 100 tokens with message: 'example message'"

    @pytest.mark.asyncio
    async def test_format_tip_with_message_anon(self, example_user: User) -> None:
        """Test formatting of an anonymous tip event message."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message="example message", isAnon=True),
            ),
            id="event_1",
        )
        message = format_message(event)
        assert (
            message == "example_user tipped 100 tokens anonymously with message: 'example message'"
        )

    @pytest.mark.asyncio
    async def test_format_tip_message_no_message(self, example_user: User) -> None:
        """Test formatting of a tip event message with no message."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message="", isAnon=False),
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user tipped 100 tokens"

    @pytest.mark.asyncio
    async def test_format_media(self, example_user: User, media_photos: Media) -> None:
        """Test formatting of a media event message."""
        event = Event(
            method="mediaPurchase",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                media=media_photos,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user purchased photos set: 'photoset1' for 25 tokens"

    @pytest.mark.asyncio
    async def test_format_message(self, example_user: User, message_example: Message) -> None:
        """Test formatting of a message event message."""
        event = Event(
            method="privateMessage",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                message=message_example,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user sent message: example message"

    @pytest.mark.asyncio
    async def test_format_user_enter(self, example_user: User) -> None:
        """Test formatting of a user enter event message."""
        event = Event(
            method="userEnter",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user entered the room"

    @pytest.mark.asyncio
    async def test_format_user_leave(self, example_user: User) -> None:
        """Test formatting of a user leave event message."""
        event = Event(
            method="userLeave",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user left the room"

    @pytest.mark.asyncio
    async def test_format_follow(self, example_user: User) -> None:
        """Test formatting of a follow event message."""
        event = Event(
            method="follow",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user followed"

    @pytest.mark.asyncio
    async def test_format_unfollow(self, example_user: User) -> None:
        """Test formatting of an unfollow event message."""
        event = Event(
            method="unfollow",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user unfollowed"

    @pytest.mark.asyncio
    async def test_format_fanclub_join(self, example_user: User) -> None:
        """Test formatting of a fanclub join event message."""
        event = Event(
            method="fanclubJoin",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user joined the fanclub"

    @pytest.mark.asyncio
    async def test_format_broadcast_start(self, example_user: User) -> None:
        """Test formatting of a broadcast start event message."""
        event = Event(
            method="broadcastStart",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "Broadcast started"

    @pytest.mark.asyncio
    async def test_format_room_subject_change(self, example_user: User) -> None:
        """Test formatting of a room subject change event message."""
        event = Event(
            method="roomSubjectChange",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                subject="Welcome to the room!",
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "Room subject changed to: 'Welcome to the room!'"

    @pytest.mark.asyncio
    async def test_format_message_no_user(self) -> None:
        """Test formatting of event message with no user."""
        event = Event(
            method="userEnter",
            object=EventData(broadcaster="example_broadcaster", user=None),
            id="event_1",
        )
        message = format_message(event)
        assert message is None

    @pytest.mark.asyncio
    async def test_format_tip_no_tip(self, example_user: User) -> None:
        """Test formatting of tip event with no tip data."""
        event = Event(
            method="tip",
            object=EventData(broadcaster="example_broadcaster", user=example_user, tip=None),
            id="event_1",
        )
        message = format_message(event)
        assert message is None
