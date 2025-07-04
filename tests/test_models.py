import re

import pytest
from pydantic import ValidationError

from chaturbate_poller.models.api_response import EventsAPIResponse
from chaturbate_poller.models.event import Event
from chaturbate_poller.models.event_data import EventData
from chaturbate_poller.models.media import Media
from chaturbate_poller.models.message import Message
from chaturbate_poller.models.tip import Tip
from chaturbate_poller.models.user import User


class TestModels:
    """Tests for the models."""

    def test_user_model(self, example_user: User) -> None:
        """Test the User model."""
        user = example_user
        assert user.username == "example_user"
        assert not user.in_fanclub
        assert user.gender == "m"
        assert user.has_tokens
        assert user.recent_tips == "none"
        assert not user.is_mod

    def test_message_model(self, message_example: Message) -> None:
        """Test the Message model."""
        message = message_example
        assert message.from_user == "example_user"
        assert message.message == "example message"
        assert message.color == "example_color"
        assert message.font == "example_font"
        assert message.to_user == "user"
        assert message.bg_color == "example_bg_color"

    def test_event_data_model(
        self, example_user: User, tip_example: Tip, media_photos: Media, message_example: Message
    ) -> None:
        """Test the EventData model."""
        event_data = EventData(
            broadcaster="example_broadcaster",
            user=example_user,
            tip=tip_example,
            media=media_photos,
            subject="example_subject",
            message=message_example,
        )
        assert event_data.broadcaster == "example_broadcaster"
        assert event_data.subject == "example_subject"
        if event_data.user:
            assert event_data.user.username == "example_user"
        if event_data.tip:
            assert event_data.tip.tokens == 100
        if event_data.media:
            assert event_data.media.name == "photoset1"
        if event_data.message:
            assert event_data.message.from_user == "example_user"

    def test_event_model(self, example_user: User) -> None:
        """Test the Event model."""
        event = Event(
            method="userEnter",
            object=EventData(
                broadcaster="example_broadcaster",
                user=example_user,
            ),
            id="UNIQUE_EVENT_ID",
        )
        assert event.method == "userEnter"
        if event.object.user:
            assert event.object.user.username == "example_user"

    def test_events_api_response_model(self, example_user: User) -> None:
        """Test the EventsAPIResponse model."""
        response = EventsAPIResponse(
            events=[
                Event(
                    method="userEnter",
                    object=EventData(
                        broadcaster="example_broadcaster",
                        user=example_user,
                    ),
                    id="UNIQUE_EVENT_ID",
                )
            ],
            nextUrl="https://example.com/next",
        )
        assert response.next_url == "https://example.com/next"

    def test_validate_tokens(self) -> None:
        """Test validation of Tip model."""
        error_pattern = re.escape(
            "1 validation error for Tip\n"
            "tokens\n"
            "  Input should be greater than or equal to 1 "
            "[type=greater_than_equal, input_value=-1, input_type=int]"
        )
        with pytest.raises(ValueError, match=error_pattern):
            Tip(tokens=-1, isAnon=False, message="Invalid tip")

    def test_validate_next_url(self) -> None:
        """Test validation of next URL."""
        error_pattern = re.escape(
            "1 validation error for EventsAPIResponse\n"
            "nextUrl\n"
            "  String should match pattern '^https?://' "
            "[type=string_pattern_mismatch, input_value='invalid_url', input_type=str]\n"
        )
        with pytest.raises(ValueError, match=error_pattern):
            EventsAPIResponse(events=[], nextUrl="invalid_url")

    def test_validate_recent_tips(self) -> None:
        """Test validation of User model."""
        error_pattern = re.escape(
            "1 validation error for User\n"
            "recentTips\n"
            "  String should match pattern '^(none|some|few|lots|tons)$' "
            "[type=string_pattern_mismatch, input_value='invalid', input_type=str]\n"
        )
        with pytest.raises(ValueError, match=error_pattern):
            User(
                username="example_user",
                inFanclub=False,
                gender="m",
                hasTokens=True,
                recentTips="invalid",
                isMod=False,
            )

    def test_validate_media_type(self) -> None:
        """Test validation of Media model."""
        error_pattern = re.escape(
            "1 validation error for Media\n"
            "type\n"
            "  String should match pattern '^(photos|video)$' "
            "[type=string_pattern_mismatch, input_value='invalid', input_type=str]\n"
        )
        with pytest.raises(ValueError, match=error_pattern):
            Media(id=1, name="photoset1", type="invalid", tokens=25)

    def test_validate_event_method(self, example_user: User) -> None:
        """Test validation of Event model."""
        # Test should verify that invalid method raises a validation error
        # without depending on the exact pattern order since we now generate it dynamically
        with pytest.raises(ValidationError) as exc_info:
            Event(
                method="invalid",
                object=EventData(
                    broadcaster="example_broadcaster",
                    user=example_user,
                ),
                id="UNIQUE_EVENT_ID",
            )

        # Verify it's the right type of validation error
        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "string_pattern_mismatch"
        assert error.errors()[0]["input"] == "invalid"

    def test_message_is_private_message(self, private_message_example: Message) -> None:
        """Test the Message model type."""
        message = private_message_example
        assert message.from_user is not None
        assert message.to_user is not None
        assert message.is_private_message
        assert not message.is_chat_message

    def test_message_is_chat_message(self, chat_message_example: Message) -> None:
        """Test the Message model type."""
        message = chat_message_example
        assert message.to_user is None
        assert not message.is_private_message
        assert message.is_chat_message
