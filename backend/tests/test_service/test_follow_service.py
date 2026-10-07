from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from business_object.follow import Follow
from business_object.user import User
from service.follow_service import FollowService
from utils.exceptions import ConflictError, NotFoundError

followed_list = [
    User(user_id=2, username="Cecile", email="c@mail.fr", password_hash="h1", bio="bio c"),
    User(user_id=5, username="Anne", email="a@mail.fr", password_hash="h2", bio="bio a"),
]


# ---------------------------------------------------------------- get_following


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_following_ok(mock_user_service, mock_follow_dao):
    """The user exists and follows several users"""

    # GIVEN
    user_id = 1
    mock_user_service.return_value.find_by_id = MagicMock(return_value=MagicMock())
    mock_follow_dao.return_value.find_following = MagicMock(return_value=followed_list)

    # WHEN
    res = FollowService().get_following(user_id)

    # THEN
    assert res == followed_list
    mock_user_service.return_value.find_by_id.assert_called_once_with(user_id)
    mock_follow_dao.return_value.find_following.assert_called_once_with(user_id)


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_following_empty(mock_user_service, mock_follow_dao):
    """The user exists but follows nobody"""

    # GIVEN
    mock_user_service.return_value.find_by_id = MagicMock(return_value=MagicMock())
    mock_follow_dao.return_value.find_following = MagicMock(return_value=[])

    # WHEN
    res = FollowService().get_following(1)

    # THEN
    assert res == []


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_following_user_not_found(mock_user_service, mock_follow_dao):
    """The user does not exist: NotFoundError and the DAO is never called"""

    # GIVEN
    mock_user_service.return_value.find_by_id = MagicMock(return_value=None)
    mock_follow_dao.return_value.find_following = MagicMock()

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        FollowService().get_following(9999)

    mock_follow_dao.return_value.find_following.assert_not_called()


# ---------------------------------------------------------------- get_followers


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_followers_ok(mock_user_service, mock_follow_dao):
    """The user exists and has several followers"""

    # GIVEN
    user_id = 1
    mock_user_service.return_value.find_by_id = MagicMock(return_value=MagicMock())
    mock_follow_dao.return_value.find_followers = MagicMock(return_value=followed_list)

    # WHEN
    res = FollowService().get_followers(user_id)

    # THEN
    assert res == followed_list
    mock_user_service.return_value.find_by_id.assert_called_once_with(user_id)
    mock_follow_dao.return_value.find_followers.assert_called_once_with(user_id)
    mock_follow_dao.return_value.find_following.assert_not_called()


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_followers_empty(mock_user_service, mock_follow_dao):
    """The user exists but has no follower"""

    # GIVEN
    mock_user_service.return_value.find_by_id = MagicMock(return_value=MagicMock())
    mock_follow_dao.return_value.find_followers = MagicMock(return_value=[])

    # WHEN
    res = FollowService().get_followers(1)

    # THEN
    assert res == []


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_get_followers_user_not_found(mock_user_service, mock_follow_dao):
    """The user does not exist: NotFoundError and the DAO is never called"""

    # GIVEN
    mock_user_service.return_value.find_by_id = MagicMock(return_value=None)
    mock_follow_dao.return_value.find_followers = MagicMock()

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        FollowService().get_followers(9999)

    mock_follow_dao.return_value.find_followers.assert_not_called()


# ---------------------------------------------------------------- follow


def users_found(*existing_ids):
    """find_by_id mock: returns a user for the given ids, None otherwise"""
    return MagicMock(side_effect=lambda uid: MagicMock() if uid in existing_ids else None)


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_follow_ok(mock_user_service, mock_follow_dao):
    """Both users exist, not followed yet: the subscription is created, dated today"""

    # GIVEN
    mock_user_service.return_value.find_by_id = users_found(1, 2)
    mock_follow_dao.return_value.exists = MagicMock(return_value=False)
    mock_follow_dao.return_value.create = MagicMock(side_effect=lambda follow: follow)

    # WHEN
    res = FollowService().follow(follower_id=1, followed_id=2)

    # THEN
    assert isinstance(res, Follow)
    assert (res.follower_id, res.followed_id) == (1, 2)
    assert res.follow_date == date.today()
    mock_follow_dao.return_value.exists.assert_called_once_with(1, 2)
    mock_follow_dao.return_value.create.assert_called_once()


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_follow_followed_not_found(mock_user_service, mock_follow_dao):
    """The user to follow does not exist: NotFoundError, nothing is created"""

    # GIVEN
    mock_user_service.return_value.find_by_id = users_found(1)
    mock_follow_dao.return_value.create = MagicMock()

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        FollowService().follow(follower_id=1, followed_id=9999)

    mock_follow_dao.return_value.create.assert_not_called()


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_follow_follower_not_found(mock_user_service, mock_follow_dao):
    """The follower does not exist: NotFoundError, nothing is created"""

    # GIVEN
    mock_user_service.return_value.find_by_id = users_found(2)
    mock_follow_dao.return_value.create = MagicMock()

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        FollowService().follow(follower_id=9999, followed_id=2)

    mock_follow_dao.return_value.create.assert_not_called()


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_follow_himself(mock_user_service, mock_follow_dao):
    """A user cannot follow himself: ValueError, nothing is created"""

    # GIVEN
    mock_user_service.return_value.find_by_id = users_found(1)
    mock_follow_dao.return_value.create = MagicMock()

    # WHEN / THEN
    with pytest.raises(ValueError):
        FollowService().follow(follower_id=1, followed_id=1)

    mock_follow_dao.return_value.create.assert_not_called()


@patch("service.follow_service.FollowDao")
@patch("service.follow_service.UserService")
def test_follow_already_followed(mock_user_service, mock_follow_dao):
    """The subscription already exists: ConflictError, nothing is created"""

    # GIVEN
    mock_user_service.return_value.find_by_id = users_found(1, 2)
    mock_follow_dao.return_value.exists = MagicMock(return_value=True)
    mock_follow_dao.return_value.create = MagicMock()

    # WHEN / THEN
    with pytest.raises(ConflictError):
        FollowService().follow(follower_id=1, followed_id=2)

    mock_follow_dao.return_value.create.assert_not_called()
