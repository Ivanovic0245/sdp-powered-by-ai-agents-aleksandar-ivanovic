from .models import User


class InMemoryUserRepository:
    def __init__(self):
        self._store: dict[str, User] = {}

    def find_by_email(self, email: str) -> User | None:
        return self._store.get(email)

    def save(self, user: User) -> User:
        self._store[user.email] = user
        return user
