import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    email: str
    username: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    display_name: str = ""
    bio: str = ""
    avatar_url: str | None = None
