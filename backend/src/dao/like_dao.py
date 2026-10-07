"""Database access for likes and dislikes."""

from business_object.like import Like
from dao.db_connection import DBConnection
from dao.review_dao import ReviewDao
from dao.user_dao import UserDao
from utils.singleton import Singleton


class LikeDao(metaclass=Singleton):
    """Manage one reaction per (user, review) pair."""

    def create(self, like: Like) -> Like:
        """Insert or replace atomically, including simultaneous PUT requests."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO like_table (user_id, review_id, liked, like_date) "
                    "VALUES (%(user_id)s, %(review_id)s, %(liked)s, %(like_date)s) "
                    "ON CONFLICT (user_id, review_id) DO UPDATE SET liked = EXCLUDED.liked "
                    "RETURNING like_date;",
                    {
                        "user_id": like.user.user_id,
                        "review_id": like.review.review_id,
                        "liked": like.liked,
                        "like_date": like.like_date,
                    },
                )
                like.like_date = cursor.fetchone()["like_date"]
        return like

    def find(self, user_id: int, review_id: int) -> Like | None:
        """Find a user's reaction, or None."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT liked, like_date FROM like_table "
                    "WHERE user_id = %(user_id)s AND review_id = %(review_id)s;",
                    {"user_id": user_id, "review_id": review_id},
                )
                row = cursor.fetchone()
        if row is None:
            return None
        user = UserDao().find_by_id(user_id)
        review = ReviewDao().find_by_id(review_id)
        if user is None or review is None:
            return None
        return Like(user=user, review=review, liked=row["liked"], like_date=row["like_date"])

    def update(self, like: Like) -> bool:
        """Change the reaction, keeping its original creation date."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE like_table SET liked = %(liked)s "
                    "WHERE user_id = %(user_id)s AND review_id = %(review_id)s;",
                    {
                        "liked": like.liked,
                        "user_id": like.user.user_id,
                        "review_id": like.review.review_id,
                    },
                )
                return cursor.rowcount == 1

    def delete(self, user_id: int, review_id: int) -> bool:
        """Remove only this user's reaction."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM like_table WHERE user_id = %(user_id)s "
                    "AND review_id = %(review_id)s;",
                    {"user_id": user_id, "review_id": review_id},
                )
                return cursor.rowcount == 1

    def count_by_review(self, review_id: int) -> tuple[int, int]:
        """Return (likes, dislikes), including (0, 0)."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FILTER (WHERE liked) AS likes, "
                    "COUNT(*) FILTER (WHERE NOT liked) AS dislikes FROM like_table "
                    "WHERE review_id = %(id)s;",
                    {"id": review_id},
                )
                row = cursor.fetchone()
        return row["likes"], row["dislikes"]

    def count_received_by_user(self, user_id: int) -> tuple[int, int]:
        """Count reactions received on a user's reviews for their profile."""
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FILTER (WHERE lt.liked) AS likes, "
                    "COUNT(*) FILTER (WHERE NOT lt.liked) AS dislikes "
                    "FROM like_table lt JOIN review rv ON rv.review_id = lt.review_id "
                    "JOIN reading rd ON rd.reading_id = rv.reading_id "
                    "WHERE rd.user_id = %(id)s;",
                    {"id": user_id},
                )
                row = cursor.fetchone()
        return row["likes"], row["dislikes"]
