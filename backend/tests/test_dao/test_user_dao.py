import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.user import User
from dao.user_dao import UserDao
from utils.reset_database import ResetDatabase
from utils.security import hash_password

# Users inserted by data/pop_db_test.sql
# The schema is rebuilt before the tests, so these ids are always the same.
SEED_USERNAMES = ["Moussa", "Cécile", "Paul", "Axel", "Anne-Camille", "Arnaud"]


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def new_user(username, email=None, password="1234", bio="bio"):
    """Builds a User that is not in the database yet.

    Each test that writes to the database uses its own username, so that the
    tests never modify the seed users nor depend on each other.
    """
    return User(
        username=username,
        email=email or f"{username}@mail.fr",
        password_hash=hash_password(password, username),
        bio=bio,
    )


# ---------- find_by_id ----------


def test_find_by_id_existing():
    """Find a user by an existing id"""

    # GIVEN
    user_id = 3

    # WHEN
    user = UserDao().find_by_id(user_id)

    # THEN
    assert isinstance(user, User)
    assert user.user_id == 3
    assert user.username == "Paul"
    assert user.email == "paul.fourcade@eleve.ensai.fr"


def test_find_by_id_non_existing():
    """Find a user by a non-existing id"""

    # GIVEN
    user_id = 999999

    # WHEN
    user = UserDao().find_by_id(user_id)

    # THEN
    assert user is None


# ---------- find_by_username ----------


def test_find_by_username_existing():
    """Find a user by an existing username"""

    # GIVEN
    username = "Paul"

    # WHEN
    user = UserDao().find_by_username(username)

    # THEN
    assert isinstance(user, User)
    assert user.user_id == 3


def test_find_by_username_with_accent():
    """Find a user whose username contains an accent"""

    # GIVEN
    username = "Cécile"

    # WHEN
    user = UserDao().find_by_username(username)

    # THEN
    assert user is not None
    assert user.email == "cecile.locatelli@eleve.ensai.fr"


def test_find_by_username_non_existing():
    """Find a user by a non-existing username"""

    # GIVEN
    username = "inconnu"

    # WHEN
    user = UserDao().find_by_username(username)

    # THEN
    assert user is None


def test_find_by_username_is_case_sensitive():
    """The exact username is required: 'paul' does not find 'Paul'"""

    # GIVEN
    username = "paul"

    # WHEN
    user = UserDao().find_by_username(username)

    # THEN
    assert user is None


# ---------- find_by_email ----------


def test_find_by_email_existing():
    """Find a user by an existing email"""

    # GIVEN
    email = "paul.fourcade@eleve.ensai.fr"

    # WHEN
    user = UserDao().find_by_email(email)

    # THEN
    assert isinstance(user, User)
    assert user.username == "Paul"


def test_find_by_email_non_existing():
    """Find a user by a non-existing email"""

    # GIVEN
    email = "inconnu@mail.fr"

    # WHEN
    user = UserDao().find_by_email(email)

    # THEN
    assert user is None


# ---------- find_by_token ----------


def test_find_by_token_existing():
    """Find the user who owns a token"""

    # GIVEN
    user = UserDao().create(new_user("dao_token"))
    user.access_token = "token-dao-test"
    UserDao().update(user)

    # WHEN
    found = UserDao().find_by_token("token-dao-test")

    # THEN
    assert found is not None
    assert found.user_id == user.user_id
    assert found.access_token == "token-dao-test"


def test_find_by_token_non_existing():
    """Find nobody with an unknown token"""

    # GIVEN
    token = "token-inconnu"

    # WHEN
    user = UserDao().find_by_token(token)

    # THEN
    assert user is None


def test_find_by_token_none():
    """A None token never matches a logged-out user (access_token NULL)"""

    # GIVEN
    token = None

    # WHEN
    user = UserDao().find_by_token(token)

    # THEN
    assert user is None


# ---------- find_all ----------


def test_find_all():
    """Returns all users as User objects, sorted by username"""

    # WHEN
    users = UserDao().find_all()

    # THEN
    assert isinstance(users, list)
    for u in users:
        assert isinstance(u, User)
    usernames = [u.username for u in users]
    for username in SEED_USERNAMES:
        assert username in usernames
    assert usernames.index("Anne-Camille") < usernames.index("Paul")


# ---------- search_by_username ----------


def test_search_by_username_part():
    """Finds the usernames containing the pattern"""

    # GIVEN
    pattern = "au"

    # WHEN
    users = UserDao().search_by_username(pattern)

    # THEN
    assert {u.username for u in users} == {"Paul", "Arnaud"}


def test_search_by_username_case_insensitive():
    """The search ignores upper and lower case"""

    # GIVEN
    pattern = "AU"

    # WHEN
    users = UserDao().search_by_username(pattern)

    # THEN
    assert {u.username for u in users} == {"Paul", "Arnaud"}


def test_search_by_username_no_result():
    """Returns an empty list when nothing matches"""

    # GIVEN
    pattern = "zzz"

    # WHEN
    users = UserDao().search_by_username(pattern)

    # THEN
    assert users == []


def test_search_by_username_empty_pattern():
    """An empty pattern returns every user"""

    # GIVEN
    pattern = ""

    # WHEN
    users = UserDao().search_by_username(pattern)

    # THEN
    assert len(users) == len(UserDao().find_all())


# ---------- create ----------


def test_create_ok():
    """Successfully create a User: the database gives its user_id"""

    # GIVEN
    user = new_user("toto")

    # WHEN
    created = UserDao().create(user)

    # THEN
    assert created.user_id is not None
    found = UserDao().find_by_id(created.user_id)
    assert found.username == "toto"
    assert found.email == "toto@mail.fr"
    assert found.password_hash == hash_password("1234", "toto")
    assert found.access_token is None


def test_create_ko_username_taken():
    """Fail to create a User whose username already exists (UNIQUE)"""

    # GIVEN
    user = new_user("Paul", email="autre.paul@mail.fr")

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().create(user)


def test_create_ko_email_taken():
    """Fail to create a User whose email already exists (UNIQUE)"""

    # GIVEN
    user = new_user("toto", email="paul.fourcade@eleve.ensai.fr")

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().create(user)


def test_create_ko_missing_email():
    """Fail to create a User without email (NOT NULL)"""

    # GIVEN
    user = User(username="toto_no_email", email=None, password_hash="h")

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().create(user)


# ---------- update ----------


def test_update_ok():
    """Successfully update the email, the bio, the password and the token"""

    # GIVEN
    user = UserDao().create(new_user("toto_update"))
    user.email = "toto_update_new@mail.fr"
    user.bio = "nouvelle bio"
    user.password_hash = hash_password("nouveaumdp", "toto_update")
    user.access_token = "token-toto-update"

    # WHEN
    update_ok = UserDao().update(user)

    # THEN
    assert update_ok
    found = UserDao().find_by_id(user.user_id)
    assert found.email == "toto_update_new@mail.fr"
    assert found.bio == "nouvelle bio"
    assert found.password_hash == hash_password("nouveaumdp", "toto_update")
    assert found.access_token == "token-toto-update"


def test_update_logout():
    """Setting access_token to None removes the token from the database"""

    # GIVEN
    user = UserDao().create(new_user("toto_logout"))
    user.access_token = "token-toto-logout"
    UserDao().update(user)
    user.access_token = None

    # WHEN
    update_ok = UserDao().update(user)

    # THEN
    assert update_ok
    assert UserDao().find_by_token("token-toto-logout") is None
    assert UserDao().find_by_id(user.user_id).access_token is None


def test_update_does_not_change_username():
    """The username is never updated: it salts the password hash"""

    # GIVEN
    user = UserDao().create(new_user("toto_keep_name"))
    user.username = "toto_new_name"

    # WHEN
    UserDao().update(user)

    # THEN
    assert UserDao().find_by_id(user.user_id).username == "toto_keep_name"


def test_update_ko_unknown_id():
    """Fail to update a User that does not exist"""

    # GIVEN
    user = User(user_id=999999, username="x", email="x@mail.fr", password_hash="h")

    # WHEN
    update_ok = UserDao().update(user)

    # THEN
    assert not update_ok


def test_update_ko_email_taken():
    """Fail to update with an email already used by another account (UNIQUE)"""

    # GIVEN
    user = UserDao().create(new_user("toto_update_email"))
    user.email = "paul.fourcade@eleve.ensai.fr"

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().update(user)


# ---------- delete ----------


def test_delete_ok():
    """Successfully delete a User"""

    # GIVEN
    user = UserDao().create(new_user("toto_delete"))

    # WHEN
    delete_ok = UserDao().delete(user.user_id)

    # THEN
    assert delete_ok
    assert UserDao().find_by_id(user.user_id) is None


def test_delete_ko_unknown_id():
    """Fail to delete a User that does not exist"""

    # GIVEN
    user_id = 999999

    # WHEN
    delete_ok = UserDao().delete(user_id)

    # THEN
    assert not delete_ok


if __name__ == "__main__":
    pytest.main([__file__])
