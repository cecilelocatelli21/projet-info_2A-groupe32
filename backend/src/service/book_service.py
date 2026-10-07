import secrets

from business_object.book import Book
from client.openlibrary_client import OpenLibraryClient
from dao.book_dao import BookDao
from utils.log_utils import log
from utils.security import hash_password


class BookService:
    """Service that handles business logic related to book (creation, search, etc.)."""

    @log
    def search(self, query: str, limit: int = 20) -> list[Book]:
        """Search a book in open library
        """
        ...

    @log
    def get_or_create_by_work_id(self, work_id) -> Book | None:
        """Get the Book if it exists in our database,
        or create the Book if the work_id is a valid reference in OL,
        if not reurn None.

        Args:
            work_id (str)
        Returns:
            Book object created or None if creation failed.
        """
        # The book already exists in our database
        book = BookDao().find_by_work_id(work_id=work_id)
        if book is not None:
            return book
        # The book (by its work_id) doesn't exist in OpenLibrary
        book = OpenLibraryClient().get_work(work_id)
        if book is None:
            return None
        # The book exists in OL, we create it in our database
        else:
            return book if BookDao().create(book) else None

    @log
    def get_book_details(self, work_id: str) -> dict | None:
        """Get the details of the book in OpenLibrary
        """
        ...


    @log
    def find_all(self) -> list[Book]:
        """Retrieves all books from the database.
        Returns:
            list[Book]"""
        return BookDao().find_all()

    @log
    def find_by_work_id(self, work_id: str) -> Book | None:
        """Finds a specific book by their unique work_id.
        work_id is the identifier from OpenLibrary we use to store books into our database

        Args:
            work_id (str)
        Returns:
            Book object if found, otherwise None.
        """
        return BookDao().find_by_work_id(work_id)

    @log
    def find_by_id(self, book_id: int) -> Book | None:
        """Finds a specific book by their book_id .
        book_id is the internal ID we use to store books into our database

        Args:
            book_id (int)
        Returns:
            Book object if found, otherwise None.
        """
        return BookDao().find_by_id(book_id)

    @log
    def search_by_author(self, author: str, limit: int = 20) -> list[Book]:
        """Get some books from the specified author
        """
        ...

    @log
    def average_rating(self, book_id: int) -> float | None:
        """Get the average rating of a book in our local database
        """
        ...

    # @log
    # def update(self, player) -> Player:
    #     """Updates an existing player's information.
    #     Args:
    #         Player object containing updated information.
    #     Returns:
    #         The updated Player object, or None if the update failed.
    #     """
    #     return player if PlayerDao().update(player) else None

    # @log
    # def delete(self, player) -> bool:
    #     """Delete a player account.
    #     Args:
    #         Player object to be deleted.
    #     Returns:
    #         True if deletion was successful, False otherwise.
    #     """
    #     return PlayerDao().delete(player)

    # @log
    # def login(self, username: str, password: str) -> Player:
    #     """Authenticates a player using their credentials.
    #     Args:
    #         username (str)
    #         password (str)
    #     Returns:
    #         Player object if authentication is successful, otherwise None.
    #     """
    #     player = PlayerDao().login(username, hash_password(password, username))
    #     if player:
    #         # Generate a token and update the Player
    #         player.access_token = secrets.token_urlsafe(32)
    #         self.update(player)
    #         return player
    #     return None

    # @log
    # def username_already_used(self, username: str) -> bool:
    #     """Check if a username is already used.
    #     Args:
    #         username (str)
    #     Returns:
    #         True if the username already exists in the database.
    #     """
    #     players = PlayerDao().find_all()
    #     return username in [p.username for p in players]
