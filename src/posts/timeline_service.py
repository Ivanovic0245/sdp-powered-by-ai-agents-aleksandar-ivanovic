from dataclasses import dataclass

from .follow_repository import InMemoryFollowRepository
from .models import Post
from .repository import InMemoryPostRepository


@dataclass
class TimelinePage:
    items: list[Post]
    page: int
    page_size: int
    has_next: bool


class TimelineService:
    def __init__(
        self,
        post_repository: InMemoryPostRepository,
        follow_repository: InMemoryFollowRepository,
    ):
        self._posts = post_repository
        self._follows = follow_repository

    def get_timeline(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> TimelinePage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        followee_ids = self._follows.get_followees(user_id)
        all_posts = self._posts.find_by_authors(followee_ids)
        all_posts.sort(key=lambda p: p.created_at, reverse=True)

        start = (page - 1) * page_size
        end = start + page_size
        page_posts = all_posts[start:end]
        has_next = len(all_posts) > end

        return TimelinePage(
            items=page_posts, page=page, page_size=page_size, has_next=has_next
        )
