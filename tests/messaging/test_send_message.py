import pytest

from src.messaging.exceptions import (
    MessageTextRequiredError,
    RecipientNotFoundError,
    UnauthorizedError,
)
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


def test_msg_be_001_s3_given_unknown_recipient_when_send_then_recipient_not_found(
    messaging, alice
):
    # GIVEN: the recipient user id does not exist in the Users Service
    unknown_id = "00000000-0000-0000-0000-000000000000"
    # WHEN: the user attempts to send a message to that id
    # THEN: RecipientNotFoundError is raised with code USER_NOT_FOUND
    with pytest.raises(RecipientNotFoundError) as exc:
        messaging.send_message_to(
            sender_id=alice.id, recipient_id=unknown_id, text="hi"
        )
    assert "USER_NOT_FOUND" in str(exc.value)


@pytest.mark.parametrize("blank", ["", "   ", "\n\t "])
def test_msg_be_001_s4_given_empty_or_whitespace_text_when_send_then_text_required(
    messaging, alice, bob, blank
):
    # GIVEN: the user submits a message with empty or whitespace-only text
    conversation = messaging.start_conversation(alice.id, bob.id)
    # WHEN: the request reaches the Messaging Service
    # THEN: MessageTextRequiredError is raised with code MESSAGE_TEXT_REQUIRED
    with pytest.raises(MessageTextRequiredError) as exc:
        messaging.send_message(
            sender_id=alice.id, conversation_id=conversation.id, text=blank
        )
    assert "MESSAGE_TEXT_REQUIRED" in str(exc.value)


def test_msg_be_001_s5_given_no_sender_when_send_then_unauthorized(
    messaging, alice, bob
):
    # GIVEN: the request carries no JWT (sender_id is absent)
    conversation = messaging.start_conversation(alice.id, bob.id)
    # WHEN: the Messaging Service is called without an authenticated sender
    # THEN: UnauthorizedError is raised (equivalent of HTTP 401)
    with pytest.raises(UnauthorizedError):
        messaging.send_message(
            sender_id=None, conversation_id=conversation.id, text="hi"
        )
