from business_object.follow import Follow
from business_object.user import User
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class FollowDao(metaclass=Singleton):
    """Class containing methods to access Follow relationships in the database."""

    @log
    def find_following(self, user_id: int) -> list[User]:
        """List the users followed by a given user.
        Args:
            user_id (int): id of the follower
        Returns:
            list[User] followed by user_id, sorted by username
            (empty list if user_id follows nobody)
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT u.*                                          "
                        "  FROM follow f                                     "
                        "  JOIN user_table u ON u.user_id = f.followed_id    "
                        "  WHERE f.follower_id = %(user_id)s                 "
                        "  ORDER BY u.username;                              ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        following_list = []

        if res:
            for row in res:
                user = User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    bio=row["bio"],
                )

                following_list.append(user)

        return following_list


    @log
    def find_followers(self, user_id: int) -> list[User]:
        """List the users who follow a given user.
        Args:
            user_id (int): id of the followed user
        Returns:
            list[User] following user_id, sorted by username
            (empty list if nobody follows user_id)
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT u.*                                          "
                        "  FROM follow f                                     "
                        "  JOIN user_table u ON u.user_id = f.follower_id    "
                        "  WHERE f.followed_id = %(user_id)s                 "
                        "  ORDER BY u.username;                              ",
                        {"user_id": user_id},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        followers_list = []

        if res:
            for row in res:
                user = User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    bio=row["bio"],
                )

                followers_list.append(user)

        return followers_list

    @log
    def exists(self, follower_id: int, followed_id: int) -> bool:
        """Check if a user already follows another user.
        Args:
            follower_id (int): id of the user who follows
            followed_id (int): id of the user being followed
        Returns:
            True if the subscription exists, False otherwise
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1                                            "
                        "  FROM follow                                       "
                        "  WHERE follower_id = %(follower_id)s               "
                        "    AND followed_id = %(followed_id)s;              ",
                        {"follower_id": follower_id, "followed_id": followed_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return res is not None

    @log
    def create(self, follow: Follow) -> Follow:
        """Create a subscription line in the database.
        Args:
            follow (Follow): the subscription to create
        Returns:
            Follow: the created subscription, with the date stored in the database
        Raises:
            psycopg2.IntegrityError: if the subscription already exists, if a user
                does not exist, or if a user tries to follow himself
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO follow(follower_id, followed_id, follow_date) VALUES "
                        "(%(follower_id)s, %(followed_id)s, %(follow_date)s) "
                        "RETURNING follow_date;",
                        {
                            "follower_id": follow.follower.user_id,
                            "followed_id": follow.followed.user_id,
                            "follow_date": follow.follow_date,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return Follow(
            follower=follow.follower,
            followed=follow.followed,
            follow_date=res["follow_date"],
        )
