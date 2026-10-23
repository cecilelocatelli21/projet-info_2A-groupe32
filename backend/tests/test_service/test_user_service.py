from unittest.mock import MagicMock

import pytest

from business_object.user import User
from dao.user_dao import UserDao
from service.user_service import UserService
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError
from utils.security import hash_password

#------------Creation of user for the tests---------------

def new_user(user_id=1, username="anne", email="anne@mail.fr", password="1234", bio="bio"):
    """Builds a new User whose password_hash matches `password`.

    A function rather than a global variable: the service modifies the users it
    receives (token, bio...), so each test gets fresh objects.
    """
    return User(
        user_id=user_id,
        username=username,
        email=email,
        password_hash=hash_password(password, username),
        bio=bio,
    )


def user_list():
    """creation of a list of user as it was a database of users"""
    return [
        new_user(user_id=1, username="anne", email="anne@mail.fr"),
        new_user(user_id=2, username="cecile", email="cecile@mail.fr"),
        new_user(user_id=3, username="paul", email="paul@mail.fr"),
    ]


# ---------- Test create_account ----------


def test_create_account_ok():
    """Successfully create an account"""

    # GIVEN
    username, email, password = "anne", "anne@mail.fr", "1234"
    UserDao().find_by_username = MagicMock(return_value=None)
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().create = MagicMock(return_value=True)

    # WHEN
    user = UserService().create_account(username, email, password)

    # THEN
    assert user.username == username
    assert user.email == email


def test_create_account_password_is_hashed():
    """The password given to the DAO is hashed, never stored in clear"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=None)
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().create = MagicMock(return_value=True)

    # WHEN
    user = UserService().create_account("anne", "anne@mail.fr", "1234")

    # THEN
    assert user.password_hash != "1234"
    assert user.password_hash == hash_password("1234", "anne")


def test_create_account_fail():
    """Fail to create an account because UserDao().create returns False"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=None)
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().create = MagicMock(return_value=False)

    # WHEN
    user = UserService().create_account("anne", "anne@mail.fr", "1234")

    # THEN
    assert user is None


def test_create_account_username_taken():
    """ConflictError when the username is already used"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=new_user())
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().create = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ConflictError):
        UserService().create_account("anne", "autre@mail.fr", "1234")
    UserDao().create.assert_not_called()


def test_create_account_email_taken():
    """ConflictError when the email is already used"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=None)
    UserDao().find_by_email = MagicMock(return_value=new_user())
    UserDao().create = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ConflictError):
        UserService().create_account("nouveau", "anne@mail.fr", "1234")
    UserDao().create.assert_not_called()

# ---------- Test username_already_used ----------


def test_username_already_used_yes():
    """The username is already used in user_list"""

    # GIVEN
    username = "cecile"
    UserDao().find_all = MagicMock(return_value=user_list())

    # WHEN
    res = UserService().username_already_used(username)

    # THEN
    assert res


def test_username_already_used_no():
    """The username is not used in user_list"""

    # GIVEN
    username = "kitten"
    UserDao().find_all = MagicMock(return_value=user_list())

    # WHEN
    res = UserService().username_already_used(username)

    # THEN
    assert not res



# ---------- Test login / logout ----------


def test_login_ok():
    """Successful login: a token is generated and saved"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=new_user(password="1234"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    user = UserService().login("anne", "1234")

    # THEN
    assert user is not None
    assert user.access_token is not None
    UserDao().update.assert_called_once_with(user) # vérifie que le sercie a bien été appelé par la méthode update une seule fois, avec l'argument user


def test_login_new_token_each_time():
    """Two logins give two different tokens"""

    # GIVEN
    UserDao().find_by_username = MagicMock(side_effect=lambda username: new_user())
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    token_1 = UserService().login("anne", "1234").access_token
    token_2 = UserService().login("anne", "1234").access_token

    # THEN
    assert token_1 != token_2


def test_login_wrong_password():
    """Fail to log in with a wrong password: no token is saved"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=new_user(password="1234"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    user = UserService().login("anne", "mauvais")

    # THEN
    assert user is None
    UserDao().update.assert_not_called()


def test_login_unknown_username():
    """Fail to log in with a username that does not exist"""

    # GIVEN
    UserDao().find_by_username = MagicMock(return_value=None)
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    user = UserService().login("inconnu", "1234")

    # THEN
    assert user is None


def test_logout():
    """The token is removed and saved"""

    # GIVEN
    user = new_user()
    user.access_token = "token-anne"
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    res = UserService().logout(user)

    # THEN
    assert res
    assert user.access_token is None
    UserDao().update.assert_called_once_with(user)


# ---------- Tests find_by_token / find_by_id / search ----------


def test_find_by_token_ok():
    """Returns the user who owns the token"""

    # GIVEN
    UserDao().find_by_token = MagicMock(return_value=new_user())

    # WHEN
    user = UserService().find_by_token("token-anne")

    # THEN
    assert user.username == "anne"


def test_find_by_token_unknown():
    """Returns None when no user owns the token"""

    # GIVEN
    UserDao().find_by_token = MagicMock(return_value=None)

    # WHEN
    user = UserService().find_by_token("faux")

    # THEN
    assert user is None


def test_find_by_id_ok():
    """Returns the user with this id"""

    # GIVEN
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=2, username="cecile"))

    # WHEN
    user = UserService().find_by_id(2)

    # THEN
    assert user.user_id == 2


def test_find_by_id_unknown():
    """Returns None when no user has this id"""

    # GIVEN
    UserDao().find_by_id = MagicMock(return_value=None)

    # WHEN
    user = UserService().find_by_id(999)

    # THEN
    assert user is None


def test_search():
    """Returns the users found by the DAO"""

    # GIVEN
    UserDao().search_by_username = MagicMock(return_value=user_list())

    # WHEN
    res = UserService().search("a")

    # THEN
    assert len(res) == 3
    UserDao().search_by_username.assert_called_once_with("a")


# ---------- Tests update_profile ----------


def test_update_profile_ok():
    """The bio and the email are changed"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1))
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    user = UserService().update_profile(current_user, 1, bio="J'aime lire", email="new@mail.fr")

    # THEN
    assert user.bio == "J'aime lire"
    assert user.email == "new@mail.fr"


def test_update_profile_none_keeps_values():
    """A field left to None is not changed"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1, bio="ancienne bio"))
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    user = UserService().update_profile(current_user, 1)

    # THEN
    assert user.bio == "ancienne bio"
    assert user.email == "anne@mail.fr"


def test_update_profile_email_taken():
    """ConflictError when the new email belongs to another account"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1))
    UserDao().find_by_email = MagicMock(
        return_value=new_user(user_id=2, username="cecile", email="cecile@mail.fr")
    )
    UserDao().update = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ConflictError):
        UserService().update_profile(current_user, 1, email="cecile@mail.fr")
    UserDao().update.assert_not_called()


def test_update_profile_other_account():
    """ForbiddenError when modifying someone else's account"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=2, username="cecile"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ForbiddenError):
        UserService().update_profile(current_user, 2, bio="piratage")
    UserDao().update.assert_not_called()


def test_update_profile_unknown_user():
    """NotFoundError when no user has this id"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=None)
    UserDao().update = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        UserService().update_profile(current_user, 999, bio="x")


def test_update_profile_fail():
    """Returns None when UserDao().update returns False"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1))
    UserDao().find_by_email = MagicMock(return_value=None)
    UserDao().update = MagicMock(return_value=False)

    # WHEN
    user = UserService().update_profile(current_user, 1, bio="x")

    # THEN
    assert user is None


# ---------- change_password ----------


def test_change_password_ok():
    """The new password is hashed and saved"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1, password="1234"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN
    res = UserService().change_password(current_user, 1, "1234", "nouveaumdp")

    # THEN
    assert res
    saved_user = UserDao().update.call_args.args[0]
    assert saved_user.password_hash == hash_password("nouveaumdp", "anne")


def test_change_password_wrong_old_password():
    """ValueError when the old password is wrong"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1, password="1234"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ValueError):
        UserService().change_password(current_user, 1, "mauvais", "nouveaumdp")
    UserDao().update.assert_not_called()


def test_change_password_other_account():
    """ForbiddenError when changing someone else's password"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=2, username="cecile"))
    UserDao().update = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ForbiddenError):
        UserService().change_password(current_user, 2, "1234", "nouveaumdp")
    UserDao().update.assert_not_called()


# ---------- Tests delete_account ----------


def test_delete_account_ok():
    """The account is deleted"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=1))
    UserDao().delete = MagicMock(return_value=True)

    # WHEN
    res = UserService().delete_account(current_user, 1)

    # THEN
    assert res
    UserDao().delete.assert_called_once_with(1)


def test_delete_account_other_account():
    """ForbiddenError when deleting someone else's account"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=new_user(user_id=2, username="cecile"))
    UserDao().delete = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(ForbiddenError):
        UserService().delete_account(current_user, 2)
    UserDao().delete.assert_not_called()


def test_delete_account_unknown_user():
    """NotFoundError when no user has this id"""

    # GIVEN
    current_user = new_user(user_id=1)
    UserDao().find_by_id = MagicMock(return_value=None)
    UserDao().delete = MagicMock(return_value=True)

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        UserService().delete_account(current_user, 999)
    UserDao().delete.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
