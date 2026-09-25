class Book:
    """
    Class representing a Book.

    book_id is our internal key (independent from Open Library).
    work_id is the work identifier provided by Open Library.

    Attributes:
        book_id (int, optional): The unique internal identifier for the book.
        work_id (str): The Open Library work identifier.
        title (str): The book's title.
        authors (str): The book's author(s).
        cover_url (str, optional): URL of the book's cover image,
            when available.
    """

    def __init__(
        self,
        work_id,
        title,
        authors,
        cover_url=None,
        book_id=None,
    ):
        """Constructor"""
        self.book_id = book_id
        self.work_id = work_id
        self.title = title
        self.authors = authors
        self.cover_url = cover_url

    def __str__(self):
        """Returns a string representation of the book.

        Returns:
            str: A string containing the title and author(s).
        """
        return f"Book({self.title}, authors: {self.authors})"

    def as_list(self) -> list[str]:
        """Returns the book's key attributes as a list.

        Returns:
            list[str]: A list containing [title, authors, cover_url].
        """
        return [self.title, self.authors, self.cover_url]