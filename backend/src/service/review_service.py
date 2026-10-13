"""Business rules for writing and managing reviews."""

from datetime import date

from psycopg2.errors import UniqueViolation

from business_object.review import Review
from business_object.user import User
from dao.book_dao import BookDao
from dao.review_dao import ReviewDao
from service.reading_service import ReadingService
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError


class ReviewService:
    """Only the reading's owner may write, edit or delete its review."""

    def __init__(self):
        self.review_dao = ReviewDao()
        self.reading_service = ReadingService()
        self.book_dao = BookDao()

    @staticmethod
    def _validate_text(text: str) -> str:
        """Reject blank text, including whitespace-only input."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Review text must not be empty.")
        return text.strip()

    def write_review(self, user: User, reading_id: int, text: str) -> Review:
        """Check existence, ownership, final status and uniqueness, in that order."""
        reading = self.reading_service.find_by_id(reading_id)
        if reading is None:
            raise NotFoundError(f"Reading (id={reading_id}) not found.")
        if reading.user.user_id != user.user_id:
            raise ForbiddenError("You can only review your own readings.")
        if reading.status not in ("read", "abandoned"):
            raise ValueError("A review requires a read or abandoned reading.")
        if self.review_dao.find_by_reading(reading_id) is not None:
            raise ConflictError("This reading already has a review.")
        review = Review(
            reading=reading, text=self._validate_text(text), publication_date=date.today()
        )
        try:
            return self.review_dao.create(review)
        except UniqueViolation as exc:
            # Another request may have inserted a review after our existence check.
            raise ConflictError("This reading already has a review.") from exc

    def find_by_id(self, review_id: int) -> Review | None:
        """Find a review, or None."""
        return self.review_dao.find_by_id(review_id)

    def get_by_reading(self, reading_id: int) -> Review | None:
        """Find a reading's review, or None."""
        return self.review_dao.find_by_reading(reading_id)

    def get_by_user(self, user_id: int) -> list[Review]:
        """List an author's reviews."""
        return self.review_dao.find_by_user(user_id)

    def get_by_book(self, work_id: str) -> list[Review]:
        """Translate Open Library's work ID to the local book ID."""
        book = self.book_dao.find_by_work_id(work_id)
        if book is None:
            return []
        return self.review_dao.find_by_book(book.book_id)

    def _owned_review(self, user: User, review_id: int) -> Review:
        """Find the review and verify that the acting user is its author."""
        review = self.find_by_id(review_id)
        if review is None:
            raise NotFoundError(f"Review (id={review_id}) not found.")
        if review.reading.user.user_id != user.user_id:
            raise ForbiddenError("Only the author may change this review.")
        return review

    def update_review(self, user: User, review_id: int, text: str) -> Review:
        """Update text without changing its author, reading or publication date."""
        review = self._owned_review(user, review_id)
        review.text = self._validate_text(text)
        if not self.review_dao.update(review):
            raise NotFoundError(f"Review (id={review_id}) no longer exists.")
        return review

    def delete_review(self, user: User, review_id: int) -> bool:
        """Delete an author's review and its cascading reactions."""
        self._owned_review(user, review_id)
        if not self.review_dao.delete(review_id):
            raise NotFoundError(f"Review (id={review_id}) no longer exists.")
        return True
