from business_object.book import Book
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class BookDao(metaclass=Singleton):
    """Class containing methods to access Books in the database."""

    @log
    def create(self, book: Book) -> bool:
        """Create a book in the database.
        Args:
            Book to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO book(work_id, title, authors, cover_url) VALUES "
                        "(%(work_id)s, %(title)s, %(authors)s, %(cover_url)s) "
                        "RETURNING book_id;",
                        {
                            "work_id": book.work_id,
                            "title": book.title,
                            "authors": book.authors,
                            "cover_url": book.cover_url,
                        }
                    )
                    connection.commit()
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            book.book_id = res["book_id"]  # Add a book_id to the book business object
            created = True

        return created

    def _row_to_book(self, row: dict) -> Book:
        return Book(
            book_id=row["book_id"],
            work_id=row["work_id"],
            title=row["title"],
            authors=row["authors"],
            cover_url=row["cover_url"]
            )

    @log
    def find_by_work_id(self, work_id: str) -> Book:
        """Find a book by their id in OpenLibrary database.
        Args:
            work_id (str): The OpenLibrary ID of the book to find
        Returns:
            Book matching the given id or None if not registered in our database
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM book                       "
                        " WHERE work_id = %(work_id)s;   ",
                        {"work_id": work_id}
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        book = None
        if row:
            book = self._row_to_book(row)

        return book

    @log
    def find_by_id(self, book_id: int) -> Book:
        """Find a book by its id in our local database.
        Args:
            book_id (int): The ID used in our local database for the book to find
        Returns:
            Book matching the given id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *"
                        "  FROM book"
                        "  WHERE book_id = %(book_id)s;",
                        {"book_id": book_id}
                    )
                    row = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return self._row_to_book(row)

    @log
    def find_all(self) -> list[Book]:
        """List all books in our local database.
        Returns:
            list[Book] sorted by book_id
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *"
                        "  FROM book"
                        "  ORDER BY book_id;"
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        books_list = []

        if res:
            for row in res:
                books_list.append(self._row_to_book(row))

        return books_list

    # @log
    # def update(self, player) -> bool:
    #     """Update a player in the database.
    #     Args:
    #         Player to be updated
    #     Returns:
    #         True if update is successful, False otherwise
    #     """
    #     nb_affected_rows = 0

    #     try:
    #         with DBConnection().connection as connection:
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     "UPDATE player                                                  "
    #                     "   SET username = %(username)s,                                "
    #                     "       password = COALESCE(%(password)s, password),            "
    #                     "       elo = %(elo)s,                                          "
    #                     "       email = %(email)s,                                      "
    #                     "       pokemon_fan = %(pokemon_fan)s,                          "
    #                     "       access_token = COALESCE(%(access_token)s, access_token) "
    #                     " WHERE id_player = %(id_player)s;                              ",
    #                     {
    #                         "username": player.username,
    #                         "password": player.password,
    #                         "elo": player.elo,
    #                         "email": player.email,
    #                         "pokemon_fan": player.pokemon_fan,
    #                         "access_token": player.access_token,
    #                         "id_player": player.id_player,
    #                     },
    #                 )
    #                 nb_affected_rows = cursor.rowcount
    #     except Exception as e:
    #         logger.error(e)
    #         raise

    #     return nb_affected_rows == 1

    # @log
    # def delete(self, player) -> bool:
    #     """Delete a player from the database.
    #     Args:
    #         Player to delete from the database
    #     Returns:
    #         True if the player was successfully deleted, False otherwise
    #     """
    #     try:
    #         with DBConnection().connection as connection:
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     "DELETE FROM player                               "
    #                     " WHERE id_player = %(id_player)s                 ",
    #                     {"id_player": player.id_player},
    #                 )
    #                 res = cursor.rowcount
    #     except Exception as e:
    #         logger.error(e)
    #         raise

    #     return res > 0

    # @log
    # def login(self, username: str, password: str) -> Player:
    #     """Login using username and password.
    #     Args:
    #         username (str)
    #         password (str)
    #     Returns:
    #         Player or None
    #     """
    #     res = None
    #     try:
    #         with DBConnection().connection as connection:
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     "SELECT *                               "
    #                     "  FROM player                          "
    #                     " WHERE username = %(username)s         "
    #                     "   AND password = %(password)s;        ",
    #                     {"username": username, "password": password},
    #                 )
    #                 res = cursor.fetchone()
    #     except Exception as e:
    #         logger.error(e)
    #         raise

    #     player = None

    #     if res:
    #         player = Player(
    #             username=res["username"],
    #             password=res["password"],
    #             elo=res["elo"],
    #             email=res["email"],
    #             pokemon_fan=res["pokemon_fan"],
    #             access_token=res["access_token"],
    #             id_player=res["id_player"],
    #         )

    #     return player

    # @log
    # def find_by_token(self, access_token: str) -> Player:
    #     """Find a player by their access token.
    #     Args:
    #         access_token (str): The token to search for.
    #     Returns:
    #         Player object if found, otherwise None.
    #     """
    #     if not access_token:
    #         return None

    #     res = None
    #     try:
    #         with DBConnection().connection as connection:
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     "SELECT *                                "
    #                     "  FROM player                           "
    #                     " WHERE access_token = %(token)s;        ",
    #                     {"token": access_token},
    #                 )
    #                 res = cursor.fetchone()
    #     except Exception as e:
    #         logger.error(f"Error finding player by token: {e}")
    #         raise

    #     player = None
    #     if res:
    #         player = Player(
    #             id_player=res["id_player"],
    #             username=res["username"],
    #             password=res["password"],
    #             elo=res["elo"],
    #             email=res["email"],
    #             pokemon_fan=res["pokemon_fan"],
    #             access_token=res["access_token"],
    #         )

    #     return player
