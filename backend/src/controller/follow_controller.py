# controller/follow_controller.py


from fastapi import APIRouter, Depends, HTTPException

from schema.user_model import UserPublicModel
from service.follow_service import FollowService
from utils.exceptions import NotFoundError
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
