import pytest

from src.users.repository import InMemoryUserRepository
from src.users.service import UserService

VALID_PASSWORD = "securepassword123"  # pragma: allowlist secret


@pytest.fixture
def repo():
    return InMemoryUserRepository()


@pytest.fixture
def service(repo):
    return UserService(repo)


def test_user_be_003_s1_given_authenticated_user_when_get_profile_then_fields_returned(
    service,
):
    # GIVEN: a registered, authenticated user
    registered = service.register("alice@example.com", "alice", VALID_PASSWORD)
    # WHEN: the user fetches their own profile
    profile = service.get_profile(registered.id)
    # THEN: current username, display name, bio, and avatar are returned
    assert profile.id == registered.id
    assert profile.username == "alice"
    assert profile.display_name == ""
    assert profile.bio == ""
    assert profile.avatar_url is None


def test_user_be_003_s2_given_valid_update_when_patch_profile_then_row_updated(service):
    # GIVEN: a registered user submits a valid updated display name and bio
    registered = service.register("alice@example.com", "alice", VALID_PASSWORD)
    # WHEN: PATCH /users/me is called with new values
    updated = service.update_profile(
        registered.id, display_name="Alice A.", bio="Hello world"
    )
    # THEN: the users row is updated and the updated profile is returned
    assert updated.display_name == "Alice A."
    assert updated.bio == "Hello world"
    assert service.get_profile(registered.id).display_name == "Alice A."


def test_user_be_003_s3_given_valid_avatar_when_upload_then_avatar_url_set(service):
    # GIVEN: a registered user uploads a 1 MB PNG (≤2 MB limit, allowed format)
    registered = service.register("alice@example.com", "alice", VALID_PASSWORD)
    image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * (1 * 1024 * 1024)
    # WHEN: the avatar is submitted
    updated = service.upload_avatar(
        registered.id, image_bytes, content_type="image/png"
    )
    # THEN: avatar_url is set on the user record and returned
    assert updated.avatar_url is not None
    assert updated.avatar_url.startswith("/avatars/")
    assert service.get_profile(registered.id).avatar_url == updated.avatar_url
