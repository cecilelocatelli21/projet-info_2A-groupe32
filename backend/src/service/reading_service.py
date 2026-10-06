from datetime import date

from business_object.reading import Reading
from business_object.user import User
from dao.reading_dao import ReadingDao
from service.book_service import BookService
from utils.log_utils import get_logger, log

logger = get_logger(__name__)

class ReadingService:
    """Class containing business logic for Reading."""

    def __init__(self):
        self.reading_dao = ReadingDao()
        self.book_service = BookService()

    @log
    def create(self, user: User, work_id: str,
               status: str = "to read") -> Reading:
        """Create a reading and add a book to the user's library.

        Args:
            user (User): User who wants to add the book.
            work_id (str): OpenLibrary identifier of the book.
            status (str): Initial reading status.

        Returns:
            Reading: The created reading.

        Raises:
            ValueError: If the book does not exist, is already
                in the user's library, or creation fails.
        """
        try:
            book = self.book_service.get_or_create_by_work_id(work_id)

            if book is None:
                logger.error(
                    "Book not found with work_id=%s",
                    work_id
                )
                raise ValueError(
                    f"Book with work_id '{work_id}' not found"
                )

            existing_reading = self.reading_dao.find_by_user_and_book(
                user.user_id,
                book.book_id
            )

            if existing_reading is not None:
                logger.error(
                    "Book already exists in user's library: "
                    "user_id=%s, book_id=%s",
                    user.user_id,
                    book.book_id
                )
                raise ValueError(
                    "This book is already in the user's library"
                )

            reading = Reading(
                user=user,
                book=book,
                status=status,
                date_added=date.today(),
                date_read=None,
                rating=None
            )

            created = self.reading_dao.create(reading)

            if not created:
                logger.error(
                    "Failed to create reading: user_id=%s, book_id=%s",
                    user.user_id,
                    book.book_id
                )
                raise ValueError("Reading could not be created")

            return reading

        except Exception as e:
            logger.error(e)
            raise

    @log
    def find_by_id(self, reading_id: int) -> Reading | None:
        """Find a reading by its identifier.

        Args:
            reading_id (int): Identifier of the reading.

        Returns:
            Reading | None:
                The reading if it exists, otherwise None.
        """
        try:
            return self.reading_dao.find_by_id(reading_id)

        except Exception as e:
            logger.error(e)
            raise

    @log
    def get_library(
        self,
        user_id: int,
        status: str | None = None
    ) -> list[Reading]:
        """Get the books in a user's library.

        The library can optionally be filtered by reading status.

        Args:
            user_id (int): Identifier of the user.
            status (str | None): Optional reading status used
                to filter the library.

        Returns:
            list[Reading]: List of readings belonging to the user.
        """
        return self.reading_dao.find_by_user(user_id, status)


    @log
    def update_reading(
        self,
        user: User,
        reading_id: int,
        status: str | None = None,
        rating: int | None = None,
        date_read: date | None = None
    ) -> Reading:
        """Update a reading belonging to a user.

        The user must own the reading. The rating can only be
        provided when the reading has a final status
        ('read' or 'abandoned').

        When the status becomes 'read' and no date_read is
        provided, the current date is used.

        Args:
            user (User): User requesting the update.
            reading_id (int): Identifier of the reading.
            status (str | None): New reading status.
            rating (int | None): New rating between 0 and 5.
            date_read (date | None): Date when the book was read.

        Returns:
            Reading: The updated reading.

        Raises:
            ValueError: If the reading does not exist, if the user
                does not own it, or if the update violates a
                business rule.
        """
        try:
            # 1. Find the reading
            reading = self.reading_dao.find_by_id(reading_id)

            if reading is None:
                logger.error(
                    "Reading not found: reading_id=%s",
                    reading_id
                )
                raise ValueError(
                    f"Reading with id '{reading_id}' not found"
                )

            # 2. Check ownership
            if reading.user.user_id != user.user_id:
                logger.error(
                    "User %s attempted to update reading %s "
                    "owned by user %s",
                    user.user_id,
                    reading_id,
                    reading.user.user_id
                )
                raise ValueError(
                    "You are not allowed to update this reading"
                )

            # 3. Determine the final status
            final_status = (
                status if status is not None
                else reading.status
            )

            # 4. Check rating business rule
            if rating is not None and final_status not in (
                "read",
                "abandoned"
            ):
                logger.error(
                    "Invalid rating for status=%s: reading_id=%s",
                    final_status,
                    reading_id
                )
                raise ValueError(
                    "A rating can only be given to a reading "
                    "with status 'read' or 'abandoned'"
                )

            # 5. Update status
            if status is not None:
                reading.status = status

            # 6. Update rating
            if rating is not None:
                reading.rating = rating

            # 7. Update date_read
            if date_read is not None:
                reading.date_read = date_read
            elif status == "read":
                reading.date_read = date.today()

            # 8. Save changes
            updated = self.reading_dao.update(reading)

            if not updated:
                logger.error(
                    "Failed to update reading: reading_id=%s",
                    reading_id
                )
                raise ValueError(
                    "Reading could not be updated"
                )

            return reading

        except Exception as e:
            logger.error(e)
            raise

    @log
    def delete_reading(
        self,
        user: User,
        reading_id: int
    ) -> bool:
        """Delete a reading from a user's library.

        Only the owner of the reading can delete it.

        Args:
            user (User): User requesting the deletion.
            reading_id (int): Identifier of the reading to delete.

        Returns:
            bool: True if the reading was successfully deleted.

        Raises:
            ValueError: If the reading does not exist or if the
                user does not own the reading.
        """
        try:
            # 1. Find the reading
            reading = self.reading_dao.find_by_id(reading_id)

            if reading is None:
                logger.error(
                    "Reading not found: reading_id=%s",
                    reading_id
                )
                raise ValueError(
                    f"Reading with id '{reading_id}' not found"
                )

            # 2. Check ownership
            if reading.user.user_id != user.user_id:
                logger.error(
                    "User %s attempted to delete reading %s "
                    "owned by user %s",
                    user.user_id,
                    reading_id,
                    reading.user.user_id
                )
                raise ValueError(
                    "You are not allowed to delete this reading"
                )

            # 3. Delete
            deleted = self.reading_dao.delete(reading_id)

            if not deleted:
                logger.error(
                    "Failed to delete reading: reading_id=%s",
                    reading_id
                )
                raise ValueError(
                    "Reading could not be deleted"
                )

            return True

        except Exception as e:
            logger.error(e)
            raise
