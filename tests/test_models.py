# ruff: noqa: S101
"""Tests for the models module."""

import pytest
from pydantic import ValidationError

from chaturbate_poller.models import Event, EventData, Gender, Media, MediaType, Message, Tip, User


@pytest.mark.parametrize(
    ("username", "in_fanclub", "gender", "has_tokens", "recent_tips", "is_mod"),
    [
        ("example_user", False, Gender.MALE, True, "none", False),
        ("test_user", True, Gender.FEMALE, False, "few", True),
    ],
)
def test_user_model(username, in_fanclub, gender, has_tokens, recent_tips, is_mod) -> None:  # noqa: ANN001, PLR0913
    """Test User model."""
    user = User(
        username=username,
        inFanclub=in_fanclub,
        gender=gender,
        hasTokens=has_tokens,
        recentTips=recent_tips,
        isMod=is_mod,
    )
    assert user.username == username
    assert user.in_fanclub == in_fanclub
    assert user.gender == gender
    assert user.has_tokens == has_tokens
    assert user.recent_tips == recent_tips
    assert user.is_mod == is_mod


def test_invalid_user_model() -> None:
    """Test invalid User model."""
    with pytest.raises(ValidationError):
        User(
            username="example_user",
            inFanclub="not_a_boolean",  # type: ignore[arg-type]
            gender=Gender.MALE,
            hasTokens=True,
            recentTips="none",
            isMod=False,
        )


def test_message_model() -> None:
    """Test Message model."""
    message = Message(
        fromUser="example_user",
        message="example message",
        color="example_color",
        font="example_font",
        toUser="user",
        bgColor="example_bg_color",
    )
    assert message.from_user == "example_user"
    assert message.message == "example message"
    assert message.color == "example_color"
    assert message.font == "example_font"
    assert message.to_user == "user"
    assert message.bg_color == "example_bg_color"


def test_invalid_message_model() -> None:
    """Test invalid Message model."""
    with pytest.raises(ValidationError):
        Message(
            fromUser="example_user",
            message=123,  # type: ignore[arg-type]
            color="example_color",
            font="example_font",
            toUser="user",
            bgColor="example_bg_color",
        )


@pytest.mark.parametrize(
    ("broadcaster", "user", "tip", "media", "subject", "message"),
    [
        (
            "example_broadcaster",
            User(
                username="example_user",
                inFanclub=False,
                gender=Gender.MALE,
                hasTokens=True,
                recentTips="none",
                isMod=False,
            ),
            Tip(tokens=100, message="example message", isAnon=False),
            Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25),
            "example subject",
            Message(
                fromUser="example_user",
                message="example message",
                color="example_color",
                font="example_font",
                toUser="user",
                bgColor="example_bg_color",
            ),
        ),
        (None, None, None, None, None, None),
    ],
)
def test_event_data_model(broadcaster, user, tip, media, subject, message) -> None:  # noqa: ANN001, PLR0913
    """Test EventData model."""
    event_data = EventData(
        broadcaster=broadcaster,
        user=user,
        tip=tip,
        media=media,
        subject=subject,
        message=message,
    )
    if user:
        assert event_data.user.username == user.username  # type: ignore[union-attr]
    if tip:
        assert event_data.tip.tokens == tip.tokens  # type: ignore[union-attr]
    if media:
        assert event_data.media.id == media.id  # type: ignore[union-attr]
    if message:
        assert event_data.message.from_user == message.from_user  # type: ignore[union-attr]
    assert event_data.broadcaster == broadcaster
    assert event_data.subject == subject


def test_invalid_event_data_model() -> None:
    """Test invalid EventData model."""
    with pytest.raises(ValidationError):
        EventData(
            broadcaster="example_broadcaster",
            user="not_a_user",  # type: ignore[arg-type]
            tip=Tip(tokens=100, message="example message", isAnon=False),
            media=Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25),
            subject="example subject",
            message=Message(
                fromUser="example_user",
                message="example message",
                color="example_color",
                font="example_font",
                toUser="user",
                bgColor="example_bg_color",
            ),
        )


def test_event_model() -> None:
    """Test Event model."""
    event = Event(
        method="userEnter",
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
        ),
        id="UNIQUE_EVENT_ID",
    )
    assert event.method == "userEnter"
    assert event.object.broadcaster == "example_broadcaster"
    if event.object.user is not None:
        assert event.object.user.username == "example_user"
    assert event.id == "UNIQUE_EVENT_ID"


def test_invalid_event_model() -> None:
    """Test invalid Event model."""
    with pytest.raises(ValidationError):
        Event(
            method="userEnter",
            object="not_an_event_data",  # type: ignore[arg-type]
            id="UNIQUE_EVENT_ID",
        )


def test_tip_model() -> None:
    """Test Tip model."""
    tip = Tip(tokens=100, message="example message", isAnon=False)
    assert tip.tokens == 100  # noqa: PLR2004
    assert tip.message == "example message"
    assert tip.is_anon is False


def test_invalid_tip_model() -> None:
    """Test invalid Tip model."""
    with pytest.raises(ValidationError):
        Tip(tokens=-1, message="example message", isAnon=False)


def test_media_model() -> None:
    """Test Media model."""
    media = Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)
    assert media.id == 1
    assert media.name == "photoset1"
    assert media.type == MediaType.PHOTOS
    assert media.tokens == 25  # noqa: PLR2004


def test_invalid_media_model() -> None:
    """Test invalid Media model."""
    with pytest.raises(ValidationError):
        Media(id="not_an_integer", name="photoset1", type=MediaType.PHOTOS, tokens=25)  # type: ignore[arg-type]
