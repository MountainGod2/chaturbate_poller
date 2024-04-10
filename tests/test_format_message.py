"""Tests for format_messages module."""

import pytest
from chaturbate_poller.format_messages import format_message, format_user_event
from chaturbate_poller.models import (
    Event,
    EventData,
    Gender,
    Media,
    MediaType,
    Message,
    Tip,
    User,
)


@pytest.mark.asyncio()
async def test_media_purchase_event() -> None:
    """Tests formatting for media purchase event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    media_type = MediaType.PHOTOS
    media = Media(id=1, name="photoset1", type=media_type, tokens=25)
    event_data = EventData(broadcaster="example_broadcaster", user=user, media=media)
    event = Event(method="mediaPurchase", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user purchased photos set: photoset1"


@pytest.mark.asyncio()
async def test_tip_event() -> None:
    """Tests formatting for tip event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    tip = Tip(tokens=100, message="example message", isAnon=False)
    event_data = EventData(broadcaster="example_broadcaster", user=user, tip=tip)
    event = Event(method="tip", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert (
        formatted_message
        == "example_user tipped 100 tokens with message: 'example message'"
    )


@pytest.mark.asyncio()
async def test_room_subject_change_event() -> None:
    """Tests formatting for room subject change event."""
    event_data = EventData(broadcaster="example_broadcaster", subject="example subject")
    event = Event(method="roomSubjectChange", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Room Subject changed to example subject"


@pytest.mark.asyncio()
async def test_message_event() -> None:
    """Tests formatting for message event."""
    chat_message = Message(
        fromUser="example_user",
        message="example message",
        color="example_color",
        font="example_font",
        toUser="user",
        bgColor="example_bg_color",
    )
    event_data = EventData(broadcaster="example_broadcaster", message=chat_message)
    event = Event(method="chatMessage", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user sent message: example message"


@pytest.mark.asyncio()
async def test_fanclub_join_event() -> None:
    """Tests formatting for fanclub join event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="example_broadcaster", user=user)
    event = Event(method="fanclubJoin", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user joined the fanclub"


@pytest.mark.asyncio()
async def test_user_enter_event() -> None:
    """Tests formatting for user join event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="example_broadcaster", user=user)
    event = Event(method="userEnter", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user entered the room"


@pytest.mark.asyncio()
async def test_user_leave_event() -> None:
    """Tests formatting for user leave event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )

    event_data = EventData(broadcaster="example_broadcaster", user=user)
    event = Event(method="userLeave", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user left the room"


@pytest.mark.asyncio()
async def test_follow_event() -> None:
    """Tests formatting for follow event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="example_broadcaster", user=user)
    event = Event(method="follow", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user followed"


@pytest.mark.asyncio()
async def test_unfollow_event() -> None:
    """Tests formatting for unfollow event."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="example_broadcaster", user=user)
    event = Event(method="unfollow", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user unfollowed"


@pytest.mark.asyncio()
async def test_broadcast_start_event() -> None:
    """Tests formatting for broadcast start event."""
    event = Event(method="broadcastStart", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Broadcast started"


@pytest.mark.asyncio()
async def test_broadcast_stop_event() -> None:
    """Tests formatting for broadcast stop event."""
    event = Event(method="broadcastStop", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Broadcast stopped"


@pytest.mark.asyncio()
async def test_unknown_event() -> None:
    """Tests formatting for unknown event."""
    event = Event(method="unknown", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown method: unknown"


@pytest.mark.asyncio()
async def test_tip_no_message() -> None:
    """Tests formatting for tip with no message."""
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    tip = Tip(tokens=100, message="", isAnon=False)
    event_data = EventData(broadcaster="example_broadcaster", user=user, tip=tip)
    event = Event(method="tip", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "example_user tipped 100 tokens "


@pytest.mark.asyncio()
async def test_tip_anon() -> None:
    """Tests formatting for tip with anonymous user."""
    tip = Tip(tokens=100, message="example message", isAnon=True)
    user = User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="example_broadcaster", user=user, tip=tip)
    event = Event(method="tip", object=event_data, id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert (
        formatted_message
        == "example_user tipped anonymously 100 tokens with message: 'example message'"
    )


@pytest.mark.asyncio()
async def test_unknown_tip_event() -> None:
    """Tests formatting for unknown tip event."""
    event = Event(method="tip", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown tip event"


@pytest.mark.asyncio()
async def test_unknown_message_event() -> None:
    """Tests formatting for unknown message event."""
    event = Event(method="chatMessage", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown message event"


@pytest.mark.asyncio()
async def test_unknown_room_subject_change_event() -> None:
    """Tests formatting for unknown room subject change event."""
    event = Event(method="roomSubjectChange", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Room Subject changed to unknown"


@pytest.mark.asyncio()
async def test_unknown_media_purchase_event() -> None:
    """Tests formatting for unknown media purchase event."""
    event = Event(method="mediaPurchase", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown media purchase event"


@pytest.mark.asyncio()
async def test_unknown_fanclub_join_event() -> None:
    """Tests formatting for unknown fanclub join event."""
    event = Event(method="fanclubJoin", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown user joined the fanclub"


@pytest.mark.asyncio()
async def test_unknown_user_enter_event() -> None:
    """Tests formatting for unknown user enter event."""
    event = Event(method="userEnter", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown user entered the room"


@pytest.mark.asyncio()
async def test_unknown_user_leave_event() -> None:
    """Tests formatting for unknown user leave event."""
    event = Event(method="userLeave", object=EventData(), id="UNIQUE_EVENT_ID")

    formatted_message = await format_message(event)

    assert formatted_message == "Unknown user left the room"


@pytest.mark.asyncio()
async def test_direct_unknown_user_event() -> None:
    """Tests handling of an unexpected event type directly in format_user_event."""
    user = User(
        username="test_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )
    event_data = EventData(broadcaster="test_broadcaster", user=user)
    event = Event(method="unexpectedUserEvent", object=event_data, id="TEST_EVENT_ID")

    formatted_message = format_user_event(event)

    assert formatted_message == "Unknown user event"
