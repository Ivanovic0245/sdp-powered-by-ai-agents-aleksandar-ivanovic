from .models import User


class InMemoryUserRepository:
    def __init__(self):
        self._store: dict[str, User] = {}

    def find_by_email(self, email: str) -> User | None:
        return self._store.get(email)

    def find_by_id(self, user_id: str) -> User | None:
        for user in self._store.values():
            if user.id == user_id:
                return user
        return None

    def find_by_username(self, username: str) -> User | None:
        for user in self._store.values():
            if user.username == username:
                return user
        return None

    def save(self, user: User) -> User:
        self._store[user.email] = user
        return user
