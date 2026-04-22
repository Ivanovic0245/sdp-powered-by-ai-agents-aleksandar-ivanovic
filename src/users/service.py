import hashlib
import secrets
from dataclasses import dataclass

from .exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidInputError,
)
from .models import User
from .repository import InMemoryUserRepository


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: str


class UserService:
    def __init__(self, repository: InMemoryUserRepository):
        self._repo = repository

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

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

        user = User(
            email=email,
            username=username,
            password_hash=self._hash_password(password),
        )
        return self._repo.save(user)

    def login(self, email: str, password: str) -> LoginResult:
        user = self._repo.find_by_email(email)
        if user is None:
            raise InvalidCredentialsError("INVALID_CREDENTIALS")
        if self._hash_password(password) != user.password_hash:
            raise InvalidCredentialsError("INVALID_CREDENTIALS")
        return LoginResult(
            access_token=secrets.token_urlsafe(32),
            refresh_token=secrets.token_urlsafe(32),
            user_id=user.id,
        )
