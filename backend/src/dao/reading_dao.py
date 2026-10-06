from business_object.reading import Reading
from dao.book_dao import BookDao
from dao.db_connection import DBConnection
from dao.user_dao import UserDao
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


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
                            "user_id": reading.user_id,
                            "book_id": reading.book_id,
                            "status": reading.status,
                            "date_added": reading.date_added,
                            "date_read": reading.date_read,
                            "rating":reading.rating
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            reading.reading_id = res["reading_id"]
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
                    user=user,
                    book=book,
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
                log.error(e)
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
    def find_by_user_and_book(self, user_id: int, book_id: int) -> Reading | None:

        """ Find a reading by user_id and book_id.
        Arg:
            user_id : int
                id permit to indentify the user.
            book_id: int
                id permit to identify the book
        Returns:
            Reading : reading of user if user_id and book_id exist in the table reading.
            None:   otherwise

        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM reading       "
                        "WHERE user_id == %(user_id)s AND book_id== %(book_id)s",
                        {
                            "user_id": user_id,
                            "book_id": book_id
                        },
                    )
                    res = cursor.fetchone() #it's expected one line because user_id and book_id are unique
        except Exception as e:
            logger.error(e)
            raise
        reading = None
        if res:
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

        return reading


    @log
    def update(self, reading: Reading) -> bool:             # status, date_read, rating
        """ Update a reading

        Arg :
            reading : Reading
        Return :
            bool :
                True if it's succesfull, false otherwise
        """

        try:
            with DBConnection.connection as connection:
                with connection.cursor as cursor:
                    cursor.excute(
                        "UPDATE INTO Reading                                        "
                        "status = %(status)s,                                                               "
                        "date_read = %(date_read)s,                                         "
                        "rating = %(rating)s)                                                       ",
                        "WHERE reading_id = %(reading_id)s;                                           ",
                        {
                            "status" : reading.status,
                            "date_read": reading.date_read,
                            "rating": reading.rating
                        },
                    )
                    nb_row = cursor.rowcount

        except Exception as e:
            logger.error(e)
            raise
        return nb_row==1

    @log
    def delete(self, reading_id: int) -> bool:
        """ Delecte reading by its id

        Arg:
            reading_id :int

        return
            bool : True if it successful and False otherwise
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE * FROM reading       "
                        "WHERE reading_id == %(reading_id)s",
                        {
                            "reading_id": reading_id
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise
        reading = False
        if res:
            reading = True
        return reading


    @log
    def average_rating_by_book(self, book_id: int) -> float | None:
        """ Average rating by book

        Arg:
            book_id : int
                id of book
        Returns:
            float: the average ration of book
            None: if book not found in table reading
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT AVG(rating) AS average_rating FROM reading       "
                        "WHERE book_id == %(book_id)s AND status IN ('read', 'abandoned')"
                        "GROUP BY book_id",
                        {
                            "book_id": book_id
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise
        avg_rating = None
        if res:
            avg_rating=res["average_rating"]
        return avg_rating

    @log
    def count_by_user(self, user_id: int) -> int | None :
        """ Count number of books in library by user_id

        Arg:
            user_id : int
                id of user
        Returns:
            int: the number of book in the library of user_id
            None: if user_id not found in table reading
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) AS nb_book FROM reading       "
                        "WHERE user_id == %(user_id)s "
                        "GROUP BY user_id",
                        {
                            "user_id": user_id
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise
        nbr_books = None
        if res:
            nbr_books=res["nb_book"]
        return nbr_books

    @log
    def find_by_users(self, user_ids: list[int],
                      min_rating: int | None = None) -> list[Reading]: # pour les recommandations
        pass
    def _row_to_reading(self, row: dict) -> Reading:        # privée
        pass
