import pytest

from src.users.exceptions import EmailAlreadyExistsError, InvalidInputError
from src.users.repository import InMemoryUserRepository
from src.users.service import UserService

VALID_PASSWORD = "securepassword123"  # pragma: allowlist secret


@pytest.fixture
def repo():
    return InMemoryUserRepository()


@pytest.fixture
def service(repo):
    return UserService(repo)


def test_user_be_001_s1_given_valid_email_when_register_then_user_created(service):
    # GIVEN: valid email, username, and password not yet registered
    # WHEN: visitor submits the registration form
    user = service.register("alice@example.com", "alice", VALID_PASSWORD)
    # THEN: a new user record is created with correct fields and a generated id
    assert user.email == "alice@example.com"
    assert user.username == "alice"
    assert user.id is not None
    assert user.password_hash != VALID_PASSWORD


def test_user_be_001_s2_given_duplicate_email_when_register_then_email_exists_error(
    service,
):
    # GIVEN: an account with the submitted email already exists
    service.register("alice@example.com", "alice", VALID_PASSWORD)
    # WHEN: visitor submits the registration form again with the same email
    # THEN: EmailAlreadyExistsError raised (maps to 409 Conflict EMAIL_ALREADY_EXISTS)
    with pytest.raises(EmailAlreadyExistsError):
        service.register("alice@example.com", "alice2", "anotherpassword")


def test_user_be_001_s3_given_invalid_email_format_when_register_then_invalid_input(
    service,
):
    # GIVEN: visitor submits a registration form with a malformed email
    # WHEN: the request reaches the Users Service
    # THEN: InvalidInputError is raised (maps to 422 Unprocessable Entity)
    with pytest.raises(InvalidInputError) as exc_info:
        service.register("notanemail", "alice", VALID_PASSWORD)
    assert exc_info.value.field == "email"


def test_user_be_001_s3_given_short_password_when_register_then_invalid_input(
    service,
):
    # GIVEN: visitor submits a registration form with a password that is too short
    # WHEN: the request reaches the Users Service
    # THEN: InvalidInputError raised with field=password (maps to 422)
    with pytest.raises(InvalidInputError) as exc_info:
        service.register("alice@example.com", "alice", "short")
    assert exc_info.value.field == "password"
