from datetime import date

from business_object.user import User


class Follow:
    """
    Business object representing a subscription between two users.

    follower is the user who follows, followed is the user being
    followed. A follow relationship is not necessarily reciprocal.
    It mirrors the `follow` table, whose primary key is
    (follower_id, followed_id): there is no follow_id.

    Attributes:
        follower (User): The user who follows.
        followed (User): The user being followed.
        follow_date (date): The date the follow relationship was created.
    """

    def __init__(
        self,
        follower: User,
        followed: User,
        follow_date: date,
    ):
        """Constructor"""
        self.follower = follower
        self.followed = followed
        self.follow_date = follow_date

    def __str__(self) -> str:
        """Returns a human-readable string describing the follow relationship.

        Returns:
            str: A string showing who follows whom.
        """
        return f"Follow({self.follower.username} follows {self.followed.username})"
