import pytest

from chaturbate_poller.models.event import Event
from chaturbate_poller.models.event_data import EventData
from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User
from chaturbate_poller.utils.format_messages import format_message


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

    @pytest.mark.parametrize(
        ("method", "expected_message"),
        [
            ("userEnter", "example_user entered the room"),
            ("userLeave", "example_user left the room"),
            ("follow", "example_user followed"),
            ("unfollow", "example_user unfollowed"),
            ("fanclubJoin", "example_user joined the fanclub"),
        ],
    )
    @pytest.mark.asyncio
    async def test_format_user_events(
        self, example_user: User, method: str, expected_message: str
    ) -> None:
        """Test formatting of user-related event messages."""
        event = Event(
            method=method,
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == expected_message

    @pytest.mark.parametrize(
        ("method", "expected_message"),
        [
            ("broadcastStart", "Broadcast started"),
            ("broadcastStop", "Broadcast stopped"),
        ],
    )
    @pytest.mark.asyncio
    async def test_format_broadcast_events(
        self, example_user: User, method: str, expected_message: str
    ) -> None:
        """Test formatting of broadcast event messages."""
        event = Event(
            method=method,
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == expected_message

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

    @pytest.mark.asyncio
    async def test_format_message_no_message_data(self, example_user: User) -> None:
        """Test formatting of a message event with no message data."""
        event = Event(
            method="chatMessage",
            object=EventData(broadcaster="example_broadcaster", user=example_user, message=None),
            id="event_1",
        )
        message = format_message(event)
        assert message is None

    @pytest.mark.asyncio
    async def test_format_message_no_user_data(self, message_example: Message) -> None:
        """Test formatting of a message event with no user data."""
        event = Event(
            method="chatMessage",
            object=EventData(broadcaster="example_broadcaster", user=None, message=message_example),
            id="event_1",
        )
        message = format_message(event)
        assert message is None

    @pytest.mark.asyncio
    async def test_format_tip_with_empty_message_after_cleanup(self, example_user: User) -> None:
        """Test formatting of a tip event with empty message after cleanup."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message=" | ", isAnon=False),  # Empty after cleanup
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user tipped 100 tokens"

    @pytest.mark.asyncio
    async def test_format_tip_with_whitespace_only_message(self, example_user: User) -> None:
        """Test formatting of a tip event with whitespace-only message."""
        event = Event(
            method="tip",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
                tip=Tip(tokens=100, message="   ", isAnon=False),  # Whitespace only
            ),
            id="event_1",
        )
        message = format_message(event)
        assert message == "example_user tipped 100 tokens"

    @pytest.mark.asyncio
    async def test_format_media_purchase_no_user(self, media_photos: Media) -> None:
        """Test formatting of a media purchase event with no user."""
        event = Event(
            method="mediaPurchase",
            object=EventData(broadcaster="example_broadcaster", user=None, media=media_photos),
            id="event_1",
        )
        message = format_message(event)
        assert message is None

    @pytest.mark.asyncio
    async def test_format_media_purchase_no_media(self, example_user: User) -> None:
        """Test formatting of a media purchase event with no media."""
        event = Event(
            method="mediaPurchase",
            object=EventData(broadcaster="example_broadcaster", user=example_user, media=None),
            id="event_1",
        )
        message = format_message(event)
        assert message is None

    @pytest.mark.asyncio
    async def test_format_room_subject_change_no_subject(self, example_user: User) -> None:
        """Test formatting of a room subject change event with no subject."""
        event = Event(
            method="roomSubjectChange",
            object=EventData(broadcaster="example_broadcaster", user=example_user, subject=None),
            id="event_1",
        )
        message = format_message(event)
        assert message is None
