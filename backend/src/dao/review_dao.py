"""Database access for reviews and their associated reading."""

from business_object.book import Book
from business_object.reading import Reading
from business_object.review import Review
from business_object.user import User
from dao.db_connection import DBConnection
from utils.singleton import Singleton


class ReviewDao(metaclass=Singleton):
    """Read a complete review with one join, without one query per object."""

    _SELECT = """
        SELECT rv.review_id, rv.text, rv.publication_date,
               rd.reading_id, rd.status, rd.date_added, rd.date_read, rd.rating,
               u.user_id, u.username, u.email, u.password_hash, u.bio,
               b.book_id, b.work_id, b.title, b.authors, b.cover_url
        FROM review rv
        JOIN reading rd ON rd.reading_id = rv.reading_id
        JOIN user_table u ON u.user_id = rd.user_id
        JOIN book b ON b.book_id = rd.book_id
    """

    @staticmethod
    def _row_to_review(row: dict) -> Review:
        """Build the nested objects from one joined row."""
        user = User(
            user_id=row["user_id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            bio=row["bio"],
        )
        book = Book(
            book_id=row["book_id"],
            work_id=row["work_id"],
            title=row["title"],
            authors=row["authors"],
            cover_url=row["cover_url"],
        )
        reading = Reading(
            reading_id=row["reading_id"],
            user=user,
            book=book,
            status=row["status"],
            date_added=row["date_added"],
            date_read=row["date_read"],
            rating=row["rating"],
        )
        return Review(
            review_id=row["review_id"],
            reading=reading,
            text=row["text"],
            publication_date=row["publication_date"],
        )
		@log
    def create(self, review: Review) -> Review:
        """Insert a review. The unique constraint enforces one per reading."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO review (reading_id, text, publication_date) "
                    "VALUES (%(reading_id)s, %(text)s, %(publication_date)s) "
                    "RETURNING review_id;",
                    {
                        "reading_id": review.reading.reading_id,
                        "text": review.text,
                        "publication_date": review.publication_date,
                    },
                )
                review.review_id = cursor.fetchone()["review_id"]
        return review

    def _find(self, query: str, parameters: dict) -> list[Review]:
        """Execute a query whose values are passed separately from the SQL."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                rows = cursor.fetchall()
        return [self._row_to_review(row) for row in rows]

    def find_by_id(self, review_id: int) -> Review | None:
        """Find a review by its internal identifier."""
        reviews = self._find(self._SELECT + " WHERE rv.review_id = %(id)s;", {"id": review_id})
        return reviews[0] if reviews else None

    def find_by_reading(self, reading_id: int) -> Review | None:
        """Find the single review of a reading, if any."""
        reviews = self._find(self._SELECT + " WHERE rd.reading_id = %(id)s;", {"id": reading_id})
        return reviews[0] if reviews else None

    def find_by_book(self, book_id: int) -> list[Review]:
        """List a book's reviews, newest first with a stable tie-breaker."""
        return self._find(
            self._SELECT + " WHERE b.book_id = %(id)s "
            "ORDER BY rv.publication_date DESC, rv.review_id DESC;",
            {"id": book_id},
        )

    def find_by_user(self, user_id: int) -> list[Review]:
        """List an author's reviews, newest first."""
        return self._find(
            self._SELECT + " WHERE u.user_id = %(id)s "
            "ORDER BY rv.publication_date DESC, rv.review_id DESC;",
            {"id": user_id},
        )

    def count_by_user(self, user_id: int) -> int:
        """Count reviews written by a user, including zero."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM review rv "
                    "JOIN reading rd ON rd.reading_id = rv.reading_id "
                    "WHERE rd.user_id = %(id)s;",
                    {"id": user_id},
                )
                return cursor.fetchone()["total"]

    def update(self, review: Review) -> bool:
        """Change only the text, preserving the author and publication date."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE review SET text = %(text)s WHERE review_id = %(id)s;",
                    {"text": review.text, "id": review.review_id},
                )
                return cursor.rowcount == 1

    def delete(self, review_id: int) -> bool:
        """Delete a review; PostgreSQL also deletes its reactions."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM review WHERE review_id = %(id)s;", {"id": review_id})
                return cursor.rowcount == 1
