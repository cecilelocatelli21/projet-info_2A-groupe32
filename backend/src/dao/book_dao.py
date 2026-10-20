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
                            "cover_url": book.cover_url
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

    @log
    def find_popular_books(
        self, user_id: int, limit: int = 10
    ) -> list[dict]:
        """Return popular books not already in the user's library.

        Args:
            user_id: ID of the user receiving recommendations.
            limit: Maximum number of books to return.

        Returns:
            List of books with their average rating and rating count.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            b.book_id,
                            b.work_id,
                            b.title,
                            b.authors,
                            b.cover_url,
                            p.average_rating,
                            p.rating_count
                        FROM popular_books p
                        JOIN book b ON b.book_id = p.book_id
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM reading r
                            WHERE r.book_id = b.book_id
                              AND r.user_id = %(user_id)s
                        )
                        ORDER BY
                            p.average_rating DESC,
                            p.rating_count DESC,
                            b.title ASC
                        LIMIT %(limit)s;
                        """,
                        {"user_id": user_id, "limit": limit},
                    )
                    rows = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        return [dict(row) for row in rows]
