from datetime import datetime

from business_object.user import User
from business_object.review import Review


class Like:
    """
    Business object representing a user's reaction to a review.

    liked = True  -> "like"
    liked = False -> "dislike"

    Attributes:
        user (User): The user reacting to the review.
        review (Review): The review being reacted to.
        liked (bool): True for "like", False for "dislike".
        like_date (datetime): The date and time of the reaction.
    """

    def __init__(
        self,
        user: User,
        review: Review,
        liked: bool,
        like_date: datetime,
    ):
        """Constructor"""
        self.user = user
        self.review = review
        self.liked = liked
        self.like_date = like_date

    def __str__(self) -> str:
        """Returns a human-readable string describing the reaction.

        Returns:
            str: A string showing who reacted and how.
        """
        reaction = "likes" if self.liked else "dislikes"
        return f"Like({self.user.username} {reaction} the review)"