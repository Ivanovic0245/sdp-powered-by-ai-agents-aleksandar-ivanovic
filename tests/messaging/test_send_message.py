import pytest

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


def test_msg_be_001_s1_given_existing_conversation_when_send_then_message_persisted(
    messaging, alice, bob
):
    # GIVEN: alice and bob have an existing conversation
    conversation = messaging.start_conversation(alice.id, bob.id)
    # WHEN: alice submits a message in that conversation
    message = messaging.send_message(
        sender_id=alice.id, conversation_id=conversation.id, text="hi bob"
    )
    # THEN: the message is persisted with the expected fields
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.sender_id == alice.id
    assert message.text == "hi bob"


def test_msg_be_001_s2_given_no_conversation_when_send_then_conversation_created(
    messaging, alice, bob
):
    # GIVEN: no conversation exists between alice and bob; bob exists in Users Service
    # WHEN: alice sends a message to bob for the first time (no conversation_id)
    message = messaging.send_message_to(
        sender_id=alice.id, recipient_id=bob.id, text="hi bob"
    )
    # THEN: a new conversation is created and the message is persisted in it
    assert message.conversation_id is not None
    conversation = messaging.get_conversation(message.conversation_id)
    assert conversation is not None
    assert set(conversation.participant_ids) == {alice.id, bob.id}
