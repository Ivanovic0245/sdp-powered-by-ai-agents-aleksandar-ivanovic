import pytest

from src.posts.exceptions import (
    PostTextRequiredError,
    PostTextTooLongError,
    UnauthorizedError,
)
from src.posts.repository import InMemoryPostRepository
from src.posts.service import PostService


@pytest.fixture
def repo():
    return InMemoryPostRepository()


@pytest.fixture
def service(repo):
    return PostService(repo)


def test_post_be_001_s1_given_valid_jwt_and_text_when_create_then_post_created(service):
    # GIVEN: user is authenticated and post text is non-empty and within length limit
    # WHEN: user submits the post form
    post = service.create_post(author_id="user-123", text="Hello, world!")
    # THEN: post record created with author_id, text, and a generated id
    assert post.author_id == "user-123"
    assert post.text == "Hello, world!"
    assert post.id is not None


def test_post_be_001_s2_given_empty_text_when_create_then_text_required_error(service):
    # GIVEN: user submits a post with an empty text body
    # WHEN: the request reaches the Posts Service
    # THEN: PostTextRequiredError is raised (maps to 422 with POST_TEXT_REQUIRED)
    with pytest.raises(PostTextRequiredError):
        service.create_post(author_id="user-123", text="")


def test_post_be_001_s3_given_whitespace_text_when_create_then_text_required_error(
    service,
):
    # GIVEN: user submits a post with whitespace-only text
    # WHEN: the request reaches the Posts Service
    # THEN: PostTextRequiredError is raised (maps to 422 with POST_TEXT_REQUIRED)
    with pytest.raises(PostTextRequiredError):
        service.create_post(author_id="user-123", text="   ")


def test_post_be_001_s4_given_text_over_280_chars_when_create_then_too_long_error(
    service,
):
    # GIVEN: post text exceeds 280 characters
    # WHEN: the request reaches the Posts Service
    # THEN: PostTextTooLongError is raised (maps to 422 with POST_TEXT_TOO_LONG)
    with pytest.raises(PostTextTooLongError):
        service.create_post(author_id="user-123", text="x" * 281)


def test_post_be_001_s5_given_no_jwt_when_create_then_unauthorized_error(service):
    # GIVEN: request carries no JWT (author_id is None)
    # WHEN: POST /posts is called
    # THEN: UnauthorizedError is raised (maps to 401 Unauthorized)
    with pytest.raises(UnauthorizedError):
        service.create_post(author_id=None, text="Hello!")
