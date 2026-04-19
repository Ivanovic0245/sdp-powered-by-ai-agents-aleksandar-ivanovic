from datetime import datetime, timedelta, timezone

import pytest

from src.posts.follow_repository import InMemoryFollowRepository
from src.posts.models import Post
from src.posts.repository import InMemoryPostRepository
from src.posts.timeline_service import TimelineService


@pytest.fixture
def post_repo():
    return InMemoryPostRepository()


@pytest.fixture
def follow_repo():
    return InMemoryFollowRepository()


@pytest.fixture
def service(post_repo, follow_repo):
    return TimelineService(post_repo, follow_repo)


def test_post_be_002_s1_given_followees_with_posts_when_get_timeline_then_sorted_desc(
    service, post_repo, follow_repo
):
    # GIVEN: authenticated user follows a user who has published multiple posts
    follow_repo.add_follow(follower_id="user-1", followee_id="user-2")
    base = datetime.now(timezone.utc)
    older = Post(
        author_id="user-2", text="older post", created_at=base - timedelta(hours=1)
    )
    newer = Post(author_id="user-2", text="newer post", created_at=base)
    post_repo.save(older)
    post_repo.save(newer)
    # WHEN: user requests their timeline feed
    page = service.get_timeline(user_id="user-1")
    # THEN: posts are returned sorted by created_at DESC with pagination metadata
    assert len(page.items) == 2
    assert page.items[0].text == "newer post"
    assert page.items[1].text == "older post"


def test_post_be_002_s2_given_no_followees_when_get_timeline_then_empty_page(service):
    # GIVEN: authenticated user follows nobody
    # WHEN: user requests their timeline feed
    page = service.get_timeline(user_id="user-1")
    # THEN: 200 OK with empty items array and correct pagination metadata
    assert page.items == []
    assert page.page == 1
    assert page.page_size == 20
    assert page.has_next is False


def test_post_be_002_s3_given_25_posts_when_page_2_then_correct_slice(
    service, post_repo, follow_repo
):
    # GIVEN: followees have published 25 posts (more than one page of 20)
    follow_repo.add_follow(follower_id="user-1", followee_id="user-2")
    base = datetime.now(timezone.utc)
    for i in range(25):
        post_repo.save(
            Post(
                author_id="user-2",
                text=f"post {i}",
                created_at=base - timedelta(minutes=i),
            )
        )
    # WHEN: user requests page 2 with page_size=20
    page = service.get_timeline(user_id="user-1", page=2, page_size=20)
    # THEN: response contains posts 21-25 in correct order with pagination metadata
    assert len(page.items) == 5
    assert [item.text for item in page.items] == [
        "post 20",
        "post 21",
        "post 22",
        "post 23",
        "post 24",
    ]
    assert page.page == 2
    assert page.page_size == 20
    assert page.has_next is False
