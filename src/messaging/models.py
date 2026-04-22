import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Conversation:
    participant_ids: tuple[str, str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Message:
    conversation_id: str
    sender_id: str
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Mention:
    message_id: str
    target_user_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
