import pytest

from src.users.exceptions import InvalidCredentialsError
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


def test_user_be_002_s2_given_wrong_password_when_login_then_invalid_credentials(
    service,
):
    # GIVEN: registered user with known email
    service.register("alice@example.com", "alice", VALID_PASSWORD)
    # WHEN: user submits correct email with the wrong password
    # THEN: InvalidCredentialsError is raised (maps to 401 INVALID_CREDENTIALS)
    with pytest.raises(InvalidCredentialsError):
        service.login("alice@example.com", "wrongpassword")


def test_user_be_002_s3_given_unknown_email_when_login_then_invalid_credentials(
    service,
):
    # GIVEN: no user registered with the submitted email
    # WHEN: a login attempt is made for that email
    # THEN: InvalidCredentialsError is raised (same error as wrong password,
    # so the response does not leak whether the email exists)
    with pytest.raises(InvalidCredentialsError):
        service.login("ghost@example.com", VALID_PASSWORD)
