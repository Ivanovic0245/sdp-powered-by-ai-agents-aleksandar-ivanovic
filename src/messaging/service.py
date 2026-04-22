from src.users.service import UserService

from .exceptions import (
    MessageTextRequiredError,
    RecipientNotFoundError,
    UnauthorizedError,
)
from .models import Conversation, Message
from .repository import InMemoryConversationRepository, InMemoryMessageRepository


class MessagingService:
    def __init__(
        self,
        conversations: InMemoryConversationRepository,
        messages: InMemoryMessageRepository,
        users: UserService,
    ):
        self._conversations = conversations
        self._messages = messages
        self._users = users

    def start_conversation(self, user_a_id: str, user_b_id: str) -> Conversation:
        conversation = Conversation(participant_ids=(user_a_id, user_b_id))
        return self._conversations.save(conversation)

    def send_message(self, sender_id: str, conversation_id: str, text: str) -> Message:
        if not sender_id:
            raise UnauthorizedError("UNAUTHORIZED")
        if not text or not text.strip():
            raise MessageTextRequiredError("MESSAGE_TEXT_REQUIRED")
        message = Message(
            conversation_id=conversation_id, sender_id=sender_id, text=text
        )
        return self._messages.save(message)

    def send_message_to(self, sender_id: str, recipient_id: str, text: str) -> Message:
        if self._users.get_profile(recipient_id) is None:
            raise RecipientNotFoundError("USER_NOT_FOUND")
        conversation = self.start_conversation(sender_id, recipient_id)
        return self.send_message(
            sender_id=sender_id, conversation_id=conversation.id, text=text
        )

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.find_by_id(conversation_id)

    def get_messages(
        self,
        requester_id: str,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        all_msgs = self._messages.find_by_conversation(conversation_id)
        start = (page - 1) * page_size
        end = start + page_size
        items = all_msgs[start:end]
        has_next = end < len(all_msgs)
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "has_next": has_next,
        }
