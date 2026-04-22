import hashlib

from .exceptions import AvatarTooLargeError, EmailAlreadyExistsError, InvalidInputError
from .models import User
from .repository import InMemoryUserRepository


class UserService:
    def __init__(self, repository: InMemoryUserRepository):
        self._repo = repository

    def register(self, email: str, username: str, password: str) -> User:
        if not email or "@" not in email:
            raise InvalidInputError("email", "Enter a valid email address")
        if not username or not username.strip():
            raise InvalidInputError("username", "Username is required")
        if not password or len(password) < 8:
            raise InvalidInputError(
                "password", "Password must be at least 8 characters"
            )

        if self._repo.find_by_email(email):
            raise EmailAlreadyExistsError("EMAIL_ALREADY_EXISTS")

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(email=email, username=username, password_hash=password_hash)
        return self._repo.save(user)

    def get_profile(self, user_id: str) -> User | None:
        return self._repo.find_by_id(user_id)

    def resolve_username(self, username: str) -> User | None:
        return self._repo.find_by_username(username)

    def update_profile(
        self,
        user_id: str,
        display_name: str | None = None,
        bio: str | None = None,
    ) -> User:
        user = self._repo.find_by_id(user_id)
        if display_name is not None:
            user.display_name = display_name
        if bio is not None:
            user.bio = bio
        return self._repo.save(user)

    MAX_AVATAR_BYTES = 2 * 1024 * 1024

    def upload_avatar(
        self, user_id: str, image_bytes: bytes, _content_type: str
    ) -> User:
        if len(image_bytes) > self.MAX_AVATAR_BYTES:
            raise AvatarTooLargeError("AVATAR_TOO_LARGE")
        user = self._repo.find_by_id(user_id)
        user.avatar_url = f"/avatars/{user.id}"
        return self._repo.save(user)
