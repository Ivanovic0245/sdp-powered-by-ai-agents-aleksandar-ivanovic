from .exceptions import PostTextRequiredError, PostTextTooLongError, UnauthorizedError
from .models import Post
from .repository import InMemoryPostRepository

MAX_POST_LENGTH = 280


class PostService:
    def __init__(self, repository: InMemoryPostRepository):
        self._repo = repository

    def create_post(self, author_id: str | None, text: str) -> Post:
        if author_id is None:
            raise UnauthorizedError("Valid JWT required")
        if not text or not text.strip():
            raise PostTextRequiredError("POST_TEXT_REQUIRED")
        if len(text) > MAX_POST_LENGTH:
            raise PostTextTooLongError("POST_TEXT_TOO_LONG")

        post = Post(author_id=author_id, text=text)
        return self._repo.save(post)
