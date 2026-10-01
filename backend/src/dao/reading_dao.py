from business_object.reading import Reading
from dao.user_dao import UserDao
from dao.book_dao import BookDao
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton


class ReadingDao(metaclass=Singleton):
    """Class containing methods to access Reading in the database."""

    @log
    def create(self, reading: Reading) -> bool:
        """Create a reading in the database i.e add a book in library's user.
        Args:
            Reading to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO reading(user_id, book_id, status, date_added, date_read, rating) VALUES "
                        "(%(user_id)s, %(book_id)s, %(date_added)s, %(date_read)s, %(rating)s) "
                        "RETURNING reading_id;",
                        {
                            "user_id": user_id,
                            "book_id": book_id,
                            "status": status,
                            "date_added": date_added,
                            "date_read": date_read,
                            "rating":rating
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            book.reading_id = res["reading_id"]
            created = True

        return created

    @log
    def find_by_id(self, reading_id: int) -> Reading | None:
        """ Find a reading by id_reading.
        Arg:
            reading_id : int
                id permit to indentify the reading.
        Returns:
            Reading : if id_reading exist in the table reading
            None:   otherwise

        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM reading       "
                        "WHERE reading_id == %(reading_id)s",
                        {
                            "reading_id": reading_id
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise
        reading = None
        if res:
            user = UserDao().find_by_id(res["user_id"])
            book = BookDao().find_by_id(res["book_id"])
            reading = Reading(
                    reading_id=res["reading_id"],
                    user_id=res["user_id"],
                    book_id=res["book_id"],
                    status=res["status"],
                    date_added=res["date_added"],
                    date_read=res["date_read"],
                    rating=res["rating"]
            )

        return reading

        @log
        def find_by_user(self, user_id: int, status: str | None = None) -> list[Reading] | None:

            """ Find a reading by user_id and eventualy by staus's reading.
            Arg:
                user_id : int
                    id permit to indentify the reading.
            Returns:
                list[Reading] : list of reading of user if user_id exist in the table reading and take care of its status
                None:   if userd_id havn't reading yet i.e not exist in reading

            """

            try:
                with DBConnection().connection as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT * FROM reading       "
                            "WHERE user_id == %(user_id)s AND status== %(status)s",
                            {
                                "user_id": user_id,
                                "status": status
                            },
                        )
                        res = cursor.fetchall()
            except Exception as e:
                logger.error(e)
                raise
            reading_list_user = None
            if res:
                reading_list_user = []
                for reading in res:
                    user = UserDao().find_by_id(res["user_id"])
                    book = BookDao().find_by_id(res["book_id"])
                    reading = Reading(
                            reading_id=res["reading_id"],
                            user=user,
                            book=book,
                            status=res["status"],
                            date_added=res["date_added"],
                            date_read=res["date_read"],
                            rating=res["rating"]
                    )
                    reading_list_user.append(reading)

            return reading_list_user

    @log
    def find_by_user_and_book(self, user_id: int, book_id: int) -> Reading | None

        """ Find a reading by user_id and book_id.
        Arg:
            user_id : int
                id permit to indentify the reading.
        Returns:
            list[Reading] : list of reading of user if user_id exist in the table reading and take care of its status
            None:   if userd_id havn't reading yet i.e not exist in reading

        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM reading       "
                        "WHERE user_id == %(user_id)s AND status== %(status)s",
                        {
                            "user_id": user_id,
                            "status": status
                        },
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise
        reading_list_user = None
        if res:
            reading_list_user = []
            for reading in res:
                reading = Reading(
                        reading_id=res["reading_id"],
                        user_id=res["user_id"],
                        book_id=res["book_id"],
                        status=res["status"],
                        date_added=res["date_added"],
                        date_read=res["date_read"],
                        rating=res["rating"]
                )
                reading_list_user.append(reading)

        return reading_list_user








        
    def update(self, reading: Reading) -> bool             # status, date_read, rating
    def delete(self, reading_id: int) -> bool
    def average_rating_by_book(self, book_id: int) -> float | None   # pour Book
    def count_by_user(self, user_id: int) -> int                     # pour le profil
    def find_by_users(self, user_ids: list[int],
                      min_rating: int | None = None) -> list[Reading] # pour les recommandations
    def _row_to_reading(self, row: dict) -> Reading        # privée



    