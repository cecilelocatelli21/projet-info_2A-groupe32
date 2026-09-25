from datetime import datetime

from business_object.user import User


class Follow:
    """
    Business object representing a subscription between two users.

    follower is the user who follows, followed is the user being
    followed. A follow relationship is not necessarily reciprocal.

    Attributes:
        follow_id (int, optional): The unique identifier for the follow
            relationship.
        follower (User): The user who follows.
        followed (User): The user being followed.
        follow_date (datetime): The date and time the follow relationship
            was created.
    """

    def __init__(
        self,
        follower: User,
        followed: User,
        follow_date: datetime,
        follow_id: int = None,
    ):
        """Constructor"""
        self.follow_id = follow_id
        self.follower = follower
        self.followed = followed
        self.follow_date = follow_date

    def __str__(self) -> str:
        """Returns a human-readable string describing the follow relationship.

        Returns:
            str: A string showing who follows whom.
        """
        return f"Follow({self.follower.username} follows {self.followed.username})"