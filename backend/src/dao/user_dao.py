from business_object.user import User
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class UserDao(metaclass=Singleton):
    """Class containing methods to access User in the database."""

    @log
    def find_all(self) -> list[User]:
        """List all users in the database.
        Returns:
            list[User] sorted by username
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                              "
                        "  FROM user_table                           "
                        "  ORDER BY username;                  "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        users_list = []

        if res:
            for row in res:
                user = User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    bio=row["bio"]
                )

                users_list.append(user)

        return users_list

    def find_by_id(self, user_id) -> User:
        """Get one user in the database by its user_id.
        Returns:
            the User with the specific user_id
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                              "
                        "  FROM user_table                           "
                        "  WHERE user_id = %(user_id)s;                  ",
                        {"user_id": user_id}
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        user = None

        if res:
            user = User(
            user_id=res["user_id"],
            username=res["username"],
            email=res["email"],
            password_hash=res["password_hash"],
            bio=res["bio"]
        )

        return user
