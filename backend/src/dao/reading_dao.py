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
                        "(%(user_id)s, %(book_id)s, %(status)s, %(date_added)s, %(date_read)s, %(rating)s) "
                        "RETURNING reading_id;",
                        {
                            "user_id": reading.user.user_id,
                            "book_id": reading.book.book_id,
                            "status": reading.status,
                            "date_added": reading.date_added,
                            "date_read": reading.date_read,
                            "rating": reading.rating
                        }
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
                        "WHERE reading_id = %(reading_id)s",
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
    def find_by_user(
        self, user_id: int, status: str | None = None
    ) -> list[Reading]:
        """Find all readings of a user, optionally filtered by status."""

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT *
                        FROM reading
                        WHERE user_id = %(user_id)s
                          AND (%(status)s IS NULL OR status = %(status)s)
                        """,
                        {
                            "user_id": user_id,
                            "status": status,
                        },
                    )
                    rows = cursor.fetchall()

        except Exception as e:
            logger.error(e)
            raise

        reading_list = []
        for row in rows:
            user = UserDao().find_by_id(row["user_id"])
            book = BookDao().find_by_id(row["book_id"])

            reading = Reading(
                reading_id=row["reading_id"],
                user=user,
                book=book,
                status=row["status"],
                date_added=row["date_added"],
                date_read=row["date_read"],
                rating=row["rating"],
            )
            reading_list.append(reading)

        return reading_list

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
                        "WHERE user_id = %(user_id)s AND book_id= %(book_id)s",
                        {
                            "user_id": user_id,
                            "book_id": book_id
                        },
                    )
                    res = cursor.fetchone()     # it's expected one line because user_id and book_id are unique
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
    def update(self, reading: Reading) -> bool:
        """Update a reading and refresh popular books if needed."""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE reading
                        SET status = %(status)s,
                            date_read = %(date_read)s,
                            rating = %(rating)s
                        WHERE reading_id = %(reading_id)s;
                        """,
                        {
                            "reading_id": reading.reading_id,
                            "status": reading.status,
                            "date_read": reading.date_read,
                            "rating": reading.rating,
                        },
                    )

                    updated = cursor.rowcount == 1

                #     if updated:
                #         cursor.execute(
                #             "REFRESH MATERIALIZED VIEW popular_books;"
                #         )

                # connection.commit()

        except Exception:
            logger.exception(
                "Failed to update reading %s",
                reading.reading_id,
            )
            raise

        return updated

    @log
    def delete(self, reading_id: int) -> bool:
        """Delete a reading by its id."""

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM reading
                        WHERE reading_id = %(reading_id)s
                        """,
                        {"reading_id": reading_id},
                    )
                    deleted = cursor.rowcount == 1

        except Exception as e:
            logger.error(e)
            raise

        return deleted

    @log
    def average_rating_by_book(self, book_id: int) -> float | None:
        """Return the average rating of a completed book."""
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT AVG(rating) AS average_rating
                        FROM reading
                        WHERE book_id = %(book_id)s
                          AND status = 'read'
                          AND rating IS NOT NULL;
                        """,
                        {"book_id": book_id},
                    )
                    row = cursor.fetchone()
        except Exception:
            logger.exception(
                "Failed to calculate average rating for book %s",
                book_id,
            )
            raise

        if row is None or row["average_rating"] is None:
            return None

        return float(row["average_rating"])

    @log
    def count_by_user(self, user_id: int) -> int | None:
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
                        "WHERE user_id = %(user_id)s "
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
            nbr_books = res["nb_book"]
        return nbr_books

    @log
    def find_by_users(self, user_ids: list[int], min_rating: int | None = None) -> list[Reading] : # pour les recommandations
        pass

    @log
    def _row_to_reading(self, row: dict) -> Reading:        # privée
        pass
