from fastapi import APIRouter, Depends, HTTPException, Response, status

from business_object.user import User
from controller.dependencies import get_current_user
from schema.user_model import UserLoginModel
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_user_service():
    """Dependency provider."""
    return UserService()


@router.post("/login", tags=["Login"])
def login(credentials: UserLoginModel, service=Depends(get_user_service)):
    """Authenticates a user.
    Args:
        credentials: username and password.
    Returns:
        dict: containing user_id and username
    Raises:
        HTTPException: 401 error if the credentials are invalid or the user does not exist."""
    logger.info("Login")
    user = service.login(credentials.username, credentials.password)
    if user:
        return {
            "id_user": user.user_id,
            "username": user.username,
            "access_token": user.access_token,
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["Login"])
def logout(current_user: User = Depends(get_current_user), service=Depends(get_user_service)):
    """Logs out the current user by erasing their token.
    Raises:
        HTTPException: 401 if the token is missing or invalid
    """
    logger.info("Logout")
    service.logout(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)