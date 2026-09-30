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
