# controller/book_controller.py


from fastapi import APIRouter, Depends, HTTPException

from schema.book_model import BookModel, BookReadModel
from service.book_service import BookService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_user_service():
    """Dependency Injection provider for UserService."""
    return UserService()


@router.get("/", response_model=list[UserReadModel], tags=["Users"])
async def find_all_users(user_service=Depends(get_user_service)):
    """List all users.
    Returns:
        list[UserReadModel]: A list of all registered users.
    """
    logger.info("List all users")
    users_list = user_service.find_all()
    return users_list


@router.get("/{user_id}", response_model=UserReadModel, tags=["Users"])
async def user_by_id(user_id: int, user_service=Depends(get_user_service)):
    """Find a user by their unique ID.
    Args:
        user_id (int)
        user_service (UserService): The service used to interact with user data
    Returns:
        UserReadModel: The user data if found
    Raises:
        HTTPException: 404 error if the user is not found
    """
    logger.info("Find a user by id")
    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User (id={user_id}) not found.")
    return user
