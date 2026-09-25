from datetime import datetime

from business_object.reading import Reading


class Review:
    """
    Business object representing a review written by a user for one
    of their readings.

    A review is attached to a Reading (rather than directly to a
    user or a book): this guarantees that a user can only review a
    book they have actually read or abandoned.

    Attributes:
        review_id (int, optional): The unique identifier for the review.
        reading (Reading): The reading this review is about.
        text (str): The content of the review.
        publication_date (datetime): The date and time the review was
            published.
    """

    def __init__(
        self,
        reading: Reading,
        text: str,
        publication_date: datetime,
        review_id: int = None,
    ):
        """Constructor"""
        self.review_id = review_id
        self.reading = reading
        self.text = text
        self.publication_date = publication_date

    def __str__(self) -> str:
        """Returns a human-readable string describing the review.

        Returns:
            str: A string containing the book title and the review text.
        """
        return f"Review({self.reading.book.title}): {self.text}"