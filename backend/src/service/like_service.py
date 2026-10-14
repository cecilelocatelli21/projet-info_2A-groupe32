"""Business rules for reactions to reviews."""

from datetime import date

from business_object.like import Like
from business_object.review import Review
from business_object.user import User
from dao.like_dao import LikeDao
from dao.review_dao import ReviewDao
from utils.exceptions import NotFoundError


class LikeService:
    """Create, replace, remove and count reactions."""

    def __init__(self):
        self.like_dao = LikeDao()
        self.review_dao = ReviewDao()

    def _require_review(self, review_id: int) -> Review:
        """Require a review before reacting or counting its reactions."""
        review = self.review_dao.find_by_id(review_id)
        if review is None:
            raise NotFoundError(f"Review (id={review_id}) not found.")
        return review

    def react(self, user: User, review_id: int, liked: bool) -> Like:
        """Atomically create or replace a reaction; repeated PUTs stay unique."""
        review = self._require_review(review_id)
        if not isinstance(liked, bool):
            raise ValueError("liked must be a boolean.")
        # No self-like restriction was agreed in the team's plan.
        reaction = Like(user=user, review=review, liked=liked, like_date=date.today())
        return self.like_dao.create(reaction)

    def remove_reaction(self, user: User, review_id: int) -> bool:
        """Remove only the authenticated user's reaction; 404 if absent."""
        self._require_review(review_id)
        if not self.like_dao.delete(user.user_id, review_id):
            raise NotFoundError("You have no reaction on this review.")
        return True

    def count(self, review_id: int) -> tuple[int, int]:
        """Return (likes, dislikes) for an existing review."""
        self._require_review(review_id)
        return self.like_dao.count_by_review(review_id)
