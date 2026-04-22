import pytest

from src.messaging.repository import (
    InMemoryConversationRepository,
    InMemoryMentionRepository,
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
def mentions_repo():
    return InMemoryMentionRepository()


@pytest.fixture
def messaging(user_service, mentions_repo):
    return MessagingService(
        conversations=InMemoryConversationRepository(),
        messages=InMemoryMessageRepository(),
        users=user_service,
        mentions=mentions_repo,
    )


@pytest.fixture
def alice(user_service):
    return user_service.register("alice@example.com", "alice", VALID_PASSWORD)


@pytest.fixture
def bob(user_service):
    return user_service.register("bob@example.com", "bob", VALID_PASSWORD)


def test_msg_be_003_s1_given_mention_when_send_then_mention_stored(
    messaging, mentions_repo, alice, bob
):
    # GIVEN: alice mentions bob by username in a message
    conversation = messaging.start_conversation(alice.id, bob.id)
    # WHEN: the message is sent
    message = messaging.send_message(
        sender_id=alice.id,
        conversation_id=conversation.id,
        text="hey @bob how are you",
    )
    # THEN: a mention row is inserted (message_id, target_user_id)
    mentions = mentions_repo.find_by_message(message.id)
    assert len(mentions) == 1
    assert mentions[0].message_id == message.id
    assert mentions[0].target_user_id == bob.id
