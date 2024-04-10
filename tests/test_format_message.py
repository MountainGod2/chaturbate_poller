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


@pytest.fixture()
def example_user() -> User:
    return User(
        username="example_user",
        inFanclub=False,
        gender=Gender.MALE,
        hasTokens=True,
        recentTips="none",
        isMod=False,
    )


@pytest.fixture()
def media_photos() -> Media:
    return Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)


@pytest.fixture()
def tip_example() -> Tip:
    return Tip(tokens=100, message="example message", isAnon=False)


@pytest.fixture()
def message_example() -> Message:
    return Message(
        fromUser="example_user",
        message="example message",
        color="example_color",
        font="example_font",
        toUser="user",
        bgColor="example_bg_color",
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("event_method", "event_data_func", "expected_message"),
    [
        (
            "mediaPurchase",
            lambda user, media, _: EventData(
                broadcaster="example_broadcaster", user=user, media=media
            ),
            "example_user purchased photos set: photoset1",
        ),
        (
            "tip",
            lambda user, _, tip: EventData(
                broadcaster="example_broadcaster", user=user, tip=tip
            ),
            "example_user tipped 100 tokens with message: 'example message'",
        ),
        (
            "roomSubjectChange",
            lambda _, __, ___: EventData(
                broadcaster="example_broadcaster", subject="example subject"
            ),
            "Room Subject changed to example subject",
        ),
        (
            "chatMessage",
            lambda _, __, ___: EventData(
                broadcaster="example_broadcaster",
                message=Message(
                    fromUser="example_user",
                    message="example message",
                    color="red",
                    font="Arial",
                    toUser="user",
                    bgColor="white",
                ),
            ),
            "example_user sent message: example message",
        ),
        (
            "fanclubJoin",
            lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
            "example_user joined the fanclub",
        ),
        (
            "userEnter",
            lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
            "example_user entered the room",
        ),
        (
            "userLeave",
            lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
            "example_user left the room",
        ),
        (
            "follow",
            lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
            "example_user followed",
        ),
        (
            "unfollow",
            lambda user, _, __: EventData(broadcaster="example_broadcaster", user=user),
            "example_user unfollowed",
        ),
    ],
)
async def test_events(  # noqa: PLR0913
    example_user,
    media_photos,
    tip_example,
    event_method,
    event_data_func,
    expected_message,
):
    event_data = event_data_func(example_user, media_photos, tip_example)
    event = Event(method=event_method, object=event_data, id="UNIQUE_EVENT_ID")
    formatted_message = await format_message(event)
    assert formatted_message == expected_message


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "tip_message, is_anon, expected_suffix",
    [
        ("example message", False, "tipped 100 tokens with message: 'example message'"),
        ("", False, "tipped 100 tokens "),
        (
            "example message",
            True,
            "tipped anonymously 100 tokens with message: 'example message'",
        ),
    ],
)
async def test_tip_variants(
    example_user, tip_example, tip_message, is_anon, expected_suffix
):
    tip_example.message = tip_message
    tip_example.is_anon = is_anon  # Adjusted to the correct property name
    event_data = EventData(
        broadcaster="example_broadcaster", user=example_user, tip=tip_example
    )
    event = Event(method="tip", object=event_data, id="UNIQUE_EVENT_ID")
    formatted_message = await format_message(event)
    assert formatted_message == f"example_user {expected_suffix}"


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "event_method, expected_message",
    [
        ("broadcastStart", "Broadcast started"),
        ("broadcastStop", "Broadcast stopped"),
        ("unknown", "Unknown method: unknown"),
        ("tip", "Unknown tip event"),
        ("chatMessage", "Unknown message event"),
        ("roomSubjectChange", "Room Subject changed to unknown"),
        ("mediaPurchase", "Unknown media purchase event"),
        ("fanclubJoin", "Unknown user joined the fanclub"),
        ("userEnter", "Unknown user entered the room"),
        ("userLeave", "Unknown user left the room"),
    ],
)
async def test_unknown_and_special_events(event_method, expected_message):
    event = Event(method=event_method, object=EventData(), id="UNIQUE_EVENT_ID")
    formatted_message = await format_message(event)
    assert formatted_message == expected_message


def test_direct_unknown_user_event(example_user):
    event_data = EventData(broadcaster="example_broadcaster", user=example_user)
    event = Event(method="unknown", object=event_data, id="UNIQUE_EVENT_ID")
    formatted_message = format_user_event(event)
    assert formatted_message == "Unknown user event"

    