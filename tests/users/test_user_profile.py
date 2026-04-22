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
