class InMemoryFollowRepository:
    def __init__(self):
        self._follows: dict[str, list[str]] = {}

    def add_follow(self, follower_id: str, followee_id: str) -> None:
        self._follows.setdefault(follower_id, []).append(followee_id)

    def get_followees(self, user_id: str) -> list[str]:
        return self._follows.get(user_id, [])
