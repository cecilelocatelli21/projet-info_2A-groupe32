from datetime import date

from pydantic import BaseModel


# What the API returns once the subscription is created
class FollowModel(BaseModel):
    follower_id: int
    followed_id: int
    follow_date: date
