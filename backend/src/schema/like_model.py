"""Request and response contracts for reactions."""

from datetime import date

from pydantic import BaseModel, ConfigDict, StrictBool


class LikeModel(BaseModel):
    """True means like, false means dislike."""

    model_config = ConfigDict(extra="forbid")
    liked: StrictBool


class LikeReadModel(BaseModel):
    """The authenticated user's reaction."""

    review_id: int
    user_id: int
    liked: bool
    like_date: date


class LikeCountModel(BaseModel):
    """Separate totals for likes and dislikes."""

    likes: int
    dislikes: int
