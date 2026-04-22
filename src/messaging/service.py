from src.users.service import UserService

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
        message = Message(
            conversation_id=conversation_id, sender_id=sender_id, text=text
        )
        return self._messages.save(message)
