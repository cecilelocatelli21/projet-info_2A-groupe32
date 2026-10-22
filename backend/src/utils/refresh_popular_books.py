from dao.db_connection import DBConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


def refresh_popular_books() -> None:
    """Refresh the popular books materialized view."""
    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("REFRESH MATERIALIZED VIEW popular_books;")
            connection.commit()

        logger.info("Materialized view popular_books refreshed.")

    except Exception:
        logger.exception("Failed to refresh popular_books.")
        raise


if __name__ == "__main__":
    refresh_popular_books()
# actu code : cd ~/work/projet-info_2A-groupe32/backend

# PYTHONPATH=src uv run python -c \
# "from dao.reading_dao import ReadingDao; print(ReadingDao().average_rating_by_book(1))"
