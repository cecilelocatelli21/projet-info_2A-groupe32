from business_object.user import User
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class UserDao(metaclass=Singleton):
    """Class containing methods to access User in the database."""

    def _find_one(self, column: str, value) -> User | None:
        """Get the user whose column equals value.
        column always comes from this class, never from the client.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"SELECT * FROM user_table WHERE {column} = %(value)s;",  # nosec B608
                            {"value": value},
                        )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return self._row_to_user(res) if res else None


    @staticmethod
    def _row_to_user(row: dict) -> User:
        """Build a User business object from a database row."""
        return User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            bio=row["bio"],
            access_token=row["access_token"],
        )


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

        return [self._row_to_user(row) for row in res] if res else []
    @log
    def find_by_id(self, user_id: int) -> User | None:
        """Get one user by its user_id."""
        return self._find_one("user_id", user_id)

    @log
    def find_by_username(self, username: str) -> User | None:
        """Get one user by its username."""
        return self._find_one("username", username)

# recherche par morceau ou pseudo

    @log
    def search_by_username(self, pattern: str) -> list[User]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM user_table WHERE username ILIKE %(pattern)s ORDER BY username;",
                        {"pattern": f"%{pattern}%"},
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        return [self._row_to_user(row) for row in res] if res else []

# création, modification, suppression
