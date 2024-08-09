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
        if event_data.user is not None:
            assert event_data.user.username == "example_user"
            assert event_data.user.in_fanclub is False

        if event_data.tip is not None:
            assert event_data.tip.tokens == 100  # noqa: PLR2004
            assert event_data.tip.message == "example message"
            assert event_data.tip.is_anon is False

        if event_data.media is not None:
            assert event_data.media.id == 1
            assert event_data.media.name == "photoset1"
            assert event_data.media.type == MediaType.PHOTOS
            assert event_data.media.tokens == 25  # noqa: PLR2004

        if event_data.message is not None:
            assert event_data.message.from_user == "example_user"
            assert event_data.message.message == "example message"
            assert event_data.message.color == "example_color"
            assert event_data.message.font == "example_font"
            assert event_data.message.to_user == "user"
            assert event_data.message.bg_color == "example_bg_color"

        assert event_data.subject == "example subject"

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
        if event.object.user is not None:
            assert event.object.user.username == "example_user"
        assert event.id == "UNIQUE_EVENT_ID"

    def test_invalid_event_model(self) -> None:
        """Test the Event model with invalid data."""
        with pytest.raises(ValidationError):
            Event(
                method="userEnter",
                object="invalid_data",  # type: ignore[arg-type]
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
            Tip(tokens=-10, message="example message", isAnon=False)

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
            Media(id="invalid_id", name="photoset1", type=MediaType.PHOTOS, tokens=25)  # type: ignore[arg-type]

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

    def test_invalid_enum(self) -> None:
        """Test an invalid enum value."""
        with pytest.raises(ValueError, match="'invalid_gender' is not a valid Gender"):
            Gender("invalid_gender")
