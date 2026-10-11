"""Follow routes (vertical Follow).

Endpoints used:
    POST /users/{user_id}/follow
    DELETE /users/{user_id}/follow
    GET /users/{user_id}/following
    GET /users/{user_id}/followers
"""

from utils.api_client import api_client


def follow(user_id: int) -> dict:
    """The connected user follows user_id (201). 400 himself, 404 unknown, 409 already."""
    return api_client.post(f"/users/{user_id}/follow")


def unfollow(user_id: int) -> dict:
    """The connected user stops following user_id (204). 404 if not followed."""
    return api_client.delete(f"/users/{user_id}/follow")


def get_following(user_id: int) -> dict:
    """Users followed by user_id (list[UserPublicModel])."""
    return api_client.get(f"/users/{user_id}/following")


def get_followers(user_id: int) -> dict:
    """Users who follow user_id (list[UserPublicModel])."""
    return api_client.get(f"/users/{user_id}/followers")
