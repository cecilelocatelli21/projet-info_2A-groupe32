import os
from datetime import date
from unittest.mock import patch

import psycopg2
import pytest

from business_object.follow import Follow
from business_object.user import User
from dao.db_connection import DBConnection
from dao.follow_dao import FollowDao
from utils.reset_database import ResetDatabase

# Users of pop_db_test.sql (user_id follows the insertion order):
# 1 Moussa, 2 Cécile, 3 Paul, 4 Axel, 5 Anne-Camille, 6 Arnaud
#
# Follows inserted for these tests (follower_id -> followed_id):
# Paul -> Cécile, Paul -> Axel, Paul -> Arnaud, Cécile -> Paul, Moussa -> Cécile
FOLLOWS = [(3, 2), (3, 4), (3, 6), (2, 3), (1, 2)]


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


@pytest.fixture(scope="module", autouse=True)
def insert_follows(setup_test_environment):
    """Insert the follow rows used by this module, and remove them afterwards"""
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            for follower_id, followed_id in FOLLOWS:
                cursor.execute(
                    "INSERT INTO follow(follower_id, followed_id) "
                    "VALUES (%(follower_id)s, %(followed_id)s);",
                    {"follower_id": follower_id, "followed_id": followed_id},
                )
    yield
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM follow;")


def make_user(user_id: int) -> User:
    """Minimal User: only user_id is used to create a follow"""
    return User(
        user_id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@mail.fr",
        password_hash="hash",
        bio=None,
    )


def delete_follow(follower_id: int, followed_id: int):
    """Remove a follow created by a test, so that the other tests keep their data"""
    with DBConnection().connection as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM follow WHERE follower_id = %(a)s AND followed_id = %(b)s;",
                {"a": follower_id, "b": followed_id},
            )


# ---------------------------------------------------------------- find_following


def test_find_following_several():
    """A user following several users gets them sorted by username"""

    # GIVEN
    user_id = 3  # Paul

    # WHEN
    following = FollowDao().find_following(user_id)

    # THEN
    assert isinstance(following, list)
    for u in following:
        assert isinstance(u, User)
    assert [u.username for u in following] == ["Arnaud", "Axel", "Cécile"]
    assert [u.user_id for u in following] == [6, 4, 2]


def test_find_following_one():
    """A user following a single user"""

    # WHEN
    following = FollowDao().find_following(1)  # Moussa

    # THEN
    assert [u.username for u in following] == ["Cécile"]


def test_find_following_nobody():
    """A user following nobody gets an empty list"""

    # WHEN
    following = FollowDao().find_following(5)  # Anne-Camille

    # THEN
    assert following == []


def test_find_following_non_existing_user():
    """A non-existing user_id gets an empty list (the 404 is handled by the service)"""

    # WHEN
    following = FollowDao().find_following(9999999)

    # THEN
    assert following == []


def test_find_following_direction():
    """Direction check: Moussa follows Cécile, so Moussa is not in Cécile's following"""

    # WHEN
    following_cecile = FollowDao().find_following(2)  # Cécile

    # THEN
    assert [u.username for u in following_cecile] == ["Paul"]


# ---------------------------------------------------------------- find_followers


def test_find_followers_several():
    """A user followed by several users gets them sorted by username"""

    # GIVEN
    user_id = 2  # Cécile

    # WHEN
    followers = FollowDao().find_followers(user_id)

    # THEN
    assert isinstance(followers, list)
    for u in followers:
        assert isinstance(u, User)
    assert [u.username for u in followers] == ["Moussa", "Paul"]
    assert [u.user_id for u in followers] == [1, 3]


def test_find_followers_one():
    """A user followed by a single user"""

    # WHEN
    followers = FollowDao().find_followers(3)  # Paul

    # THEN
    assert [u.username for u in followers] == ["Cécile"]


def test_find_followers_nobody():
    """A user followed by nobody gets an empty list"""

    # WHEN
    followers = FollowDao().find_followers(1)  # Moussa

    # THEN
    assert followers == []


def test_find_followers_non_existing_user():
    """A non-existing user_id gets an empty list"""

    # WHEN
    followers = FollowDao().find_followers(9999999)

    # THEN
    assert followers == []


def test_following_and_followers_are_not_mixed():
    """Paul follows 3 users but has only 1 follower: the two directions differ"""

    # WHEN
    following = FollowDao().find_following(3)
    followers = FollowDao().find_followers(3)

    # THEN
    assert len(following) == 3
    assert len(followers) == 1


# ---------------------------------------------------------------- exists


def test_exists_true():
    """Paul follows Cécile"""
    assert FollowDao().exists(3, 2) is True


def test_exists_false():
    """Nobody follows in this direction: Cécile follows Paul and Moussa follows Cécile,
    but Cécile does not follow Moussa"""
    assert FollowDao().exists(2, 1) is False


def test_exists_is_directional():
    """Paul -> Axel exists, Axel -> Paul does not"""
    assert FollowDao().exists(3, 4) is True
    assert FollowDao().exists(4, 3) is False


# ---------------------------------------------------------------- create


def test_create_ok():
    """A subscription line is created and returned with its date"""

    # GIVEN
    follow = Follow(follower=make_user(5), followed=make_user(1), follow_date=date.today())

    try:
        # WHEN
        created = FollowDao().create(follow)

        # THEN
        assert isinstance(created, Follow)
        assert (created.follower.user_id, created.followed.user_id) == (5, 1)
        assert created.follow_date == date.today()
        assert FollowDao().exists(5, 1) is True
        assert [u.username for u in FollowDao().find_following(5)] == ["Moussa"]
        assert [u.username for u in FollowDao().find_followers(1)] == ["Anne-Camille"]
    finally:
        delete_follow(5, 1)


def test_create_duplicate_raises():
    """The primary key (follower_id, followed_id) forbids a duplicate"""

    # GIVEN: Paul -> Cécile already exists
    follow = Follow(follower=make_user(3), followed=make_user(2), follow_date=date.today())

    # WHEN / THEN
    with pytest.raises(psycopg2.errors.UniqueViolation):
        FollowDao().create(follow)


def test_create_self_follow_raises():
    """The CHECK (follower_id <> followed_id) forbids following oneself"""

    # GIVEN
    follow = Follow(follower=make_user(4), followed=make_user(4), follow_date=date.today())

    # WHEN / THEN
    with pytest.raises(psycopg2.errors.CheckViolation):
        FollowDao().create(follow)


def test_create_unknown_user_raises():
    """The foreign keys forbid a subscription with a non-existing user"""

    # GIVEN
    follow = Follow(follower=make_user(1), followed=make_user(9999999), follow_date=date.today())

    # WHEN / THEN
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        FollowDao().create(follow)


# ---------------------------------------------------------------- delete


def test_delete_ok():
    """An existing subscription is deleted, only in the given direction"""

    # GIVEN: Anne-Camille (5) follows Moussa (1), and Moussa follows Anne-Camille
    FollowDao().create(Follow(follower=make_user(5), followed=make_user(1), follow_date=date.today()))
    FollowDao().create(Follow(follower=make_user(1), followed=make_user(5), follow_date=date.today()))

    try:
        # WHEN
        deleted = FollowDao().delete(5, 1)

        # THEN
        assert deleted is True
        assert FollowDao().exists(5, 1) is False
        assert FollowDao().exists(1, 5) is True  # the other direction is untouched
    finally:
        delete_follow(5, 1)
        delete_follow(1, 5)


def test_delete_not_existing():
    """Deleting a subscription that does not exist returns False"""

    # Cécile (2) does not follow Moussa (1)
    assert FollowDao().delete(2, 1) is False


def test_delete_keeps_other_subscriptions():
    """Deleting Paul -> Cécile keeps Paul's other subscriptions"""

    # GIVEN
    try:
        # WHEN
        deleted = FollowDao().delete(3, 2)

        # THEN
        assert deleted is True
        assert [u.username for u in FollowDao().find_following(3)] == ["Arnaud", "Axel"]
    finally:
        FollowDao().create(Follow(follower=make_user(3), followed=make_user(2), follow_date=date.today()))
