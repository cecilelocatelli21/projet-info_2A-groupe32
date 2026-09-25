from datetime import date

from business_object.user import User
from business_object.book import Book


class Reading:
    """
    Business object representing the fact that a user has added a book
    to their library, with a reading status.

    Attributes:
        reading_id (int, optional): The unique identifier for the reading.
        user (User): The user who owns this reading.
        book (Book): The book concerned by this reading.
        status (str): Reading status ("to read", "in progress", "read",
            "abandoned").
        date_added (date): The date the book was added to the library.
        date_read (date, optional): The date the status became "read".
            Only set once the book has been read.
        rating (int, optional): Rating given to the book (0 to 5).
            Only set once the book has been read or abandoned.
    """

    def __init__(
        self,
        user: User,
        book: Book,
        status: str,
        date_added: date,
        date_read: date = None,
        rating: int = None,
        reading_id: int = None,
    ):
        """Constructor"""
        self.reading_id = reading_id
        self.user = user
        self.book = book
        self.status = status
        self.date_added = date_added
        self.date_read = date_read
        self.rating = rating

    def __str__(self) -> str:
        """Returns a human-readable string describing the reading.

        Returns:
            str: A string containing the book title, status and rating.
        """
        return (
            f"Reading({self.book.title}, status: {self.status}, "
            f"rating: {self.rating})"
        )