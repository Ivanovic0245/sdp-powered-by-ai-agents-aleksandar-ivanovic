from .models import Post


class InMemoryPostRepository:
    def __init__(self):
        self._store: list[Post] = []

    def save(self, post: Post) -> Post:
        self._store.append(post)
        return post

    def find_by_authors(self, author_ids: list[str]) -> list[Post]:
        author_id_set = set(author_ids)
        return [p for p in self._store if p.author_id in author_id_set]
