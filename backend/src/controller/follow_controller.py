# controller/follow_controller.py


from fastapi import APIRouter, Depends, HTTPException, status

from business_object.user import User
from controller.dependencies import get_current_user
from schema.follow_model import FollowModel
from schema.user_model import UserPublicModel
from service.follow_service import FollowService
from utils.exceptions import ConflictError, NotFoundError
from utils.log_utils import get_logger

# No prefix: routes are declared with their full path
router = APIRouter()

logger = get_logger(__name__)


def get_follow_service():
    """Dependency Injection provider for FollowService."""
    return FollowService()


@router.get("/users/{user_id}/following", response_model=list[UserPublicModel], tags=["Follow"])
async def get_following(
    user_id: int,
    follow_service=Depends(get_follow_service),
):
    """List the users followed by a given user.
    Args:
        user_id (int): id of the user whose subscriptions are requested
        follow_service (FollowService): The service used to interact with follow data
    Returns:
        list[UserPublicModel]: the followed users, sorted by username (empty if none)
    Raises:
        HTTPException: 404 error if the user is not found.
    """
    logger.info("List the users followed by a user")
    try:
        return follow_service.get_following(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/users/{user_id}/followers", response_model=list[UserPublicModel], tags=["Follow"])
async def get_followers(
    user_id: int,
    follow_service=Depends(get_follow_service),
):
    """List the users who follow a given user.
    Args:
        user_id (int): id of the user whose followers are requested
        follow_service (FollowService): The service used to interact with follow data
    Returns:
        list[UserPublicModel]: the followers, sorted by username (empty if none)
    Raises:
        HTTPException: 404 error if the user is not found.
    """
    logger.info("List the followers of a user")
    try:
        return follow_service.get_followers(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/users/{user_id}/follow",
    response_model=FollowModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Follow"],
)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    follow_service=Depends(get_follow_service),
):
    """The connected user follows user_id (creates a subscription line).
    The follower is always the connected user, identified by the token.
    Args:
        user_id (int): id of the user to follow (taken from the URL)
        current_user (User): the authenticated user, who becomes the follower
        follow_service (FollowService): The service used to interact with follow data
    Returns:
        FollowModel: the created subscription
    Raises:
        HTTPException: 401 error if the token is missing or invalid.
        HTTPException: 404 error if user_id is not found.
        HTTPException: 400 error if the user tries to follow himself.
        HTTPException: 409 error if the subscription already exists.
    """
    logger.info("User %s follows user %s", current_user.user_id, user_id)
    try:
        follow = follow_service.follow(user=current_user, followed_id=user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    return FollowModel(
        follower_id=follow.follower.user_id,
        followed_id=follow.followed.user_id,
        follow_date=follow.follow_date,
    )


@router.delete(
    "/users/{user_id}/follow",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Follow"],
)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    follow_service=Depends(get_follow_service),
):
    """The connected user stops following user_id (deletes the subscription line).
    The follower is always the connected user, identified by the token.
    Args:
        user_id (int): id of the user to unfollow (taken from the URL)
        current_user (User): the authenticated user, who is the follower
        follow_service (FollowService): The service used to interact with follow data
    Raises:
        HTTPException: 401 error if the token is missing or invalid.
        HTTPException: 404 error if the user does not follow user_id.
    """
    logger.info("User %s unfollows user %s", current_user.user_id, user_id)
    try:
        follow_service.unfollow(user=current_user, followed_id=user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
