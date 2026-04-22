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


def test_user_be_002_s1_given_valid_credentials_when_login_then_tokens_issued(service):
    # GIVEN: registered user with known email and password
    service.register("alice@example.com", "alice", VALID_PASSWORD)
    # WHEN: user submits correct email and password
    result = service.login("alice@example.com", VALID_PASSWORD)
    # THEN: access_token and refresh_token are issued
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.user_id is not None
