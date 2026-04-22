from .models import Conversation, Message


class InMemoryConversationRepository:
    def __init__(self):
        self._store: dict[str, Conversation] = {}

    def save(self, conversation: Conversation) -> Conversation:
        self._store[conversation.id] = conversation
        return conversation

    def find_by_id(self, conversation_id: str) -> Conversation | None:
        return self._store.get(conversation_id)


class InMemoryMessageRepository:
    def __init__(self):
        self._store: dict[str, Message] = {}

    def save(self, message: Message) -> Message:
        self._store[message.id] = message
        return message

    def find_by_conversation(self, conversation_id: str) -> list[Message]:
        return sorted(
            (m for m in self._store.values() if m.conversation_id == conversation_id),
            key=lambda m: m.created_at,
        )
