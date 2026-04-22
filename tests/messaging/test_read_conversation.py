import pytest

from src.messaging.exceptions import NotAParticipantError
from src.messaging.repository import (
    InMemoryConversationRepository,
    InMemoryMessageRepository,
)
from src.messaging.service import MessagingService
from src.users.repository import InMemoryUserRepository
from src.users.service import UserService

VALID_PASSWORD = "securepassword123"  # pragma: allowlist secret


@pytest.fixture
def user_service():
    return UserService(InMemoryUserRepository())


@pytest.fixture
def messaging(user_service):
    return MessagingService(
        conversations=InMemoryConversationRepository(),
        messages=InMemoryMessageRepository(),
        users=user_service,
    )


@pytest.fixture
def alice(user_service):
    return user_service.register("alice@example.com", "alice", VALID_PASSWORD)


@pytest.fixture
def bob(user_service):
    return user_service.register("bob@example.com", "bob", VALID_PASSWORD)


@pytest.fixture
def charlie(user_service):
    return user_service.register("charlie@example.com", "charlie", VALID_PASSWORD)


def test_msg_be_002_s1_given_participant_when_get_messages_then_sorted_asc_paginated(
    messaging, alice, bob
):
    # GIVEN: alice is a participant; conversation has multiple messages
    conversation = messaging.start_conversation(alice.id, bob.id)
    for i in range(3):
        messaging.send_message(
            sender_id=alice.id, conversation_id=conversation.id, text=f"m{i}"
        )
    # WHEN: alice opens the conversation
    result = messaging.get_messages(
        requester_id=alice.id, conversation_id=conversation.id, page=1, page_size=50
    )
    # THEN: messages are returned sorted by created_at ASC, paginated
    assert [m.text for m in result["items"]] == ["m0", "m1", "m2"]
    assert result["page"] == 1
    assert result["page_size"] == 50
    assert result["has_next"] is False


def test_msg_be_002_s2_given_non_participant_when_get_messages_then_forbidden(
    messaging, alice, bob, charlie
):
    # GIVEN: the conversation is between alice and bob; charlie is not a participant
    conversation = messaging.start_conversation(alice.id, bob.id)
    messaging.send_message(
        sender_id=alice.id, conversation_id=conversation.id, text="private"
    )
    # WHEN: charlie calls get_messages on that conversation
    # THEN: NotAParticipantError is raised with code NOT_A_PARTICIPANT
    with pytest.raises(NotAParticipantError) as exc:
        messaging.get_messages(requester_id=charlie.id, conversation_id=conversation.id)
    assert "NOT_A_PARTICIPANT" in str(exc.value)
