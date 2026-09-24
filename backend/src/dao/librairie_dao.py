from business_object.utilisateur import Utilisateur
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class UtilisateurDao(metaclass=Singleton):
    """Class containing methods to access Utilisateurs in the database."""

    @log
    def find_all(self) -> list[Utilisateur]:
        """List all users in the database.
        Returns:
            list[Utilisateur] sorted by username
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        "  FROM utilisateur                           "
                        " ORDER BY pseudo;                     "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        users_list = []

        if res:
            for row in res:
                user = Utilisateur(
                    id_user=row["id_user"],
                    pseudo=row["pseudo"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    bio=row["bio"]
                )

                users_list.append(user)

        return users_list
