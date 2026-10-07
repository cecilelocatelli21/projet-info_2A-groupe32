from business_object.book import Book
from client.openlibrary_client import OpenLibraryClient
from dao.book_dao import BookDao
from dao.reading_dao import ReadingDao
from utils.log_utils import log


class BookService:
    """Service that handles business logic related to book (creation, search, etc.)."""

    @log
    def search(self, query: str, limit: int = 20) -> list[Book]:
        """Search a book in OpenLibrary

        Args:
            query (str): the object of the search
            limit (int): maximum number of books to return
        Returns:
            list[Book] list of the books found on OpenLibrary.
        """
        return OpenLibraryClient().search(query, limit)

    @log
    def get_or_create_by_work_id(self, work_id: str) -> Book | None:
        """Get the Book if it exists in our database,
        or create the Book if the work_id is a valid reference in OL,
        if not return None.

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            Book | None: 
                the book with its book_id (found or just created),
                or None if OpenLibrary does not know this work_id
                or if the creation failed.
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
        """Get the details of the book necessary for the book page.

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            dict | None:
                None if OpenLibrary does not know this work_id
                or dict with following keys :"work_id", "book_id", "title",
                "authors", "cover_url", "subjects", "description",
                "editions", "average_rating".
        """
        # 1. Information from OpenLibrary
        client = OpenLibraryClient()
        book = client.get_work(work_id=work_id)
        if book is None:
            return None
        details = {
            "work_id": work_id,
            "book_id": None,
            "title": book.title,
            "authors": book.authors,
            "cover_url": book.cover_url,
            "subjects": [],
            "description": None,
            "editions": client.get_editions(work_id),
            "average_rating": None
            }
        # Subjects and description may be missing
        work_details = client.get_work_details(work_id)
        if work_details is not None:
            details["subjects"] = work_details.get("subjects",[])
            details["description"] = work_details.get("description")
        # 2. Information from our database
        book_in_database = BookDao().find_by_work_id(work_id)
        if book_in_database is not None:
            details["book_id"] = book_in_database.book_id
            details["average_rating"] = self.average_rating(book_in_database.book_id)
        return details




    @log
    def find_all(self) -> list[Book]:
        """Retrieves all books from the database.

        Returns:
            list[Book]"""
        return BookDao().find_all()

    @log
    def find_by_work_id(self, work_id: str) -> Book | None:
        """Finds a specific book by its unique work_id.

        Args:
            work_id (str) : OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            Book object if found, otherwise None.
        """
        return BookDao().find_by_work_id(work_id)

    @log
    def find_by_id(self, book_id: int) -> Book | None:
        """Finds a specific book by its book_id .

        Args:
            book_id (int): internal ID of the book in our database
        Returns:
            Book object if found, otherwise None.
        """
        return BookDao().find_by_id(book_id)

    @log
    def search_by_author(self, author: str, limit: int = 20) -> list[Book]:
        """Get some books from the specified author

        Args:
            author (str): name of an author
            limit (int): maximum number of books to return
        Returns:
            list[Book]: books found on OpenLibrary, with book_id = None
        """
        return OpenLibraryClient().search_by_author(author, limit)

    @log
    def average_rating(self, book_id: int) -> float | None:
        """Get the average rating of a book in our local database

        Args:
            book_id (int): internal ID of the book in our database
        Returns:
            float | None: the average rating (between 0 and 5),
                or None if no user has rated this book yet.
        """
        return ReadingDao().average_rating_by_book(book_id)


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
