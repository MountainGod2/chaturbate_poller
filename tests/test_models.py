# ruff: noqa: S101
"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from chaturbate_poller.models import Event, EventData, Gender, Media, MediaType, Message, Tip, User


class TestModels:
    """Tests for the models."""

    def test_user_model(self) -> None:
        """Test the User model."""
        user = User(
            username="example_user",
            inFanclub=False,
            gender=Gender.MALE,
            hasTokens=True,
            recentTips="none",
            isMod=False,
        )
        assert user.username == "example_user"
        assert user.in_fanclub is False
        assert user.gender == Gender.MALE
        assert user.has_tokens is True
        assert user.recent_tips == "none"
        assert user.is_mod is False

    def test_invalid_user_model(self) -> None:
        """Test the User model with invalid data."""
        with pytest.raises(ValidationError):
            User(
                username="example_user",
                inFanclub="not_a_boolean",  # type: ignore[arg-type]
                gender=Gender.MALE,
                hasTokens=True,
                recentTips="none",
                isMod=False,
            )

    def test_message_model(self) -> None:
        """Test the Message model."""
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

    def test_invalid_message_model(self) -> None:
        """Test the Message model with invalid data."""
        with pytest.raises(ValidationError):
            Message(
                fromUser="example_user",
                message=123,  # type: ignore[arg-type]
                color="example_color",
                font="example_font",
                toUser="user",
                bgColor="example_bg_color",
            )

    def test_event_data_model(self) -> None:
        """Test the EventData model."""
        event_data = EventData(
            broadcaster="example_broadcaster",
            user=User(
                username="example_user",
                inFanclub=False,
                gender=Gender.MALE,
                hasTokens=True,
                recentTips="none",
                isMod=False,
            ),
            tip=Tip(
                tokens=100,
                message="example message",
                isAnon=False,
            ),
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
        assert event_data.broadcaster == "example_broadcaster"
        assert event_data.user.username == "example_user"  # type: ignore[union-attr]
        assert event_data.tip.tokens == 100  # type: ignore[union-attr]  # noqa: PLR2004
        assert event_data.media.name == "photoset1"  # type: ignore[union-attr]
        assert event_data.subject == "example subject"
        assert event_data.message.message == "example message"  # type: ignore[union-attr]

    def test_invalid_event_data_model(self) -> None:
        """Test the EventData model with invalid data."""
        with pytest.raises(ValidationError):
            EventData(
                broadcaster="example_broadcaster",
                user="not_a_user",  # type: ignore[arg-type]
                tip=Tip(
                    tokens=100,
                    message="example message",
                    isAnon=False,
                ),
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

    def test_event_model(self) -> None:
        """Test the Event model."""
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
        assert event.object.user.username == "example_user"  # type: ignore[union-attr]
        assert event.id == "UNIQUE_EVENT_ID"

    def test_invalid_event_model(self) -> None:
        """Test the Event model with invalid data."""
        with pytest.raises(ValidationError):
            Event(
                method="userEnter",
                object="not_an_event_data",  # type: ignore[arg-type]
                id="UNIQUE_EVENT_ID",
            )

    def test_tip_model(self) -> None:
        """Test the Tip model."""
        tip = Tip(tokens=100, message="example message", isAnon=False)
        assert tip.tokens == 100  # noqa: PLR2004
        assert tip.message == "example message"
        assert tip.is_anon is False

    def test_invalid_tip_model(self) -> None:
        """Test the Tip model with invalid data."""
        with pytest.raises(ValidationError):
            Tip(tokens=-1, message="example message", isAnon=False)

    def test_media_model(self) -> None:
        """Test the Media model."""
        media = Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)
        assert media.id == 1
        assert media.name == "photoset1"
        assert media.type == MediaType.PHOTOS
        assert media.tokens == 25  # noqa: PLR2004

    def test_invalid_media_model(self) -> None:
        """Test the Media model with invalid data."""
        with pytest.raises(ValidationError):
            Media(id=1, name="photoset1", type="invalid_type", tokens=25)  # type: ignore[arg-type]

    def test_enum_gender(self) -> None:
        """Test the Gender enum."""
        assert Gender.MALE.value == "m"
        assert Gender.FEMALE.value == "f"
        assert Gender.TRANS.value == "t"
        assert Gender.COUPLE.value == "c"

    def test_enum_media_type(self) -> None:
        """Test the MediaType enum."""
        assert MediaType.PHOTOS.value == "photos"
        assert MediaType.VIDEOS.value == "videos"
