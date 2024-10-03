import pytest

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

    def test_message_model(self) -> None:
        """Test the Message model."""
        message = Message(
            fromUser="example_user",
            message="example_message",
            color="example_color",
            font="example_font",
            toUser="user",
            bgColor="example_bg_color",
        )
        assert message.from_user == "example_user"
        assert message.message == "example_message"
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
            tip=Tip(tokens=100, message="example_message", isAnon=False),
            media=Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25),
            subject="example_subject",
            message=Message(
                fromUser="example_user",
                message="example_message",
                color="example_color",
                font="example_font",
                toUser="user",
                bgColor="example_bg_color",
            ),
        )
        assert event_data.broadcaster == "example_broadcaster"

        if event_data.user:
            assert event_data.user.username == "example_user"
            assert event_data.user.in_fanclub is False

        if event_data.tip:
            assert event_data.tip.tokens == 100
            assert event_data.tip.message == "example_message"
            assert event_data.tip.is_anon is False

        if event_data.media:
            assert event_data.media.id == 1
            assert event_data.media.name == "photoset1"
            assert event_data.media.type == MediaType.PHOTOS
            assert event_data.media.tokens == 25

        if event_data.message:
            assert event_data.message.from_user == "example_user"
            assert event_data.message.message == "example_message"
            assert event_data.message.color == "example_color"
            assert event_data.message.font == "example_font"
            assert event_data.message.to_user == "user"
            assert event_data.message.bg_color == "example_bg_color"

        assert event_data.subject == "example_subject"

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

        if event.object.user:
            assert event.object.user.username == "example_user"
        assert event.id == "UNIQUE_EVENT_ID"

    def test_tip_model(self) -> None:
        """Test the Tip model."""
        tip = Tip(tokens=100, message="example message", isAnon=False)
        assert tip.tokens == 100
        assert tip.message == "example message"
        assert tip.is_anon is False

    def test_media_model(self) -> None:
        """Test the Media model."""
        media = Media(id=1, name="photoset1", type=MediaType.PHOTOS, tokens=25)
        assert media.id == 1
        assert media.name == "photoset1"
        assert media.type == MediaType.PHOTOS
        assert media.tokens == 25

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

    def test_validate_tokens_valid_value(self) -> None:
        """Test validate_tokens with a valid value."""
        valid_value = 10
        assert Tip(tokens=valid_value, isAnon=False, message="") == Tip(
            tokens=valid_value, isAnon=False, message=""
        )  # noqa: ERA001, RUF100

    def test_validate_tokens_invalid_value(self) -> None:
        """Test validate_tokens with an invalid value."""
        invalid_value = 0
        with pytest.raises(ValueError, match="Tokens must be greater than 0."):
            Tip(tokens=invalid_value, isAnon=False, message="")
        with pytest.raises(ValueError, match="Tokens must be greater than 0."):
            Tip(tokens=-1, isAnon=False, message="")
