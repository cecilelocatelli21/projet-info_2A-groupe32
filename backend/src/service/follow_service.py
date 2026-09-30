from business_object.user import User
from dao.follow_dao import FollowDao
from service.user_service import UserService
from utils.exceptions import NotFoundError
from utils.log_utils import log


class FollowService:
    """Service that handles business logic related to follows between users."""

    @log
    def get_following(self, user_id: int) -> list[User]:
        """Retrieves the users followed by a given user.
        Args:
            user_id (int): id of the user whose subscriptions are requested
        Returns:
            list[User] followed by user_id (empty list if nobody is followed)
        Raises:
            NotFoundError: if user_id does not match any user
        """
        if UserService().find_by_id(user_id) is None:
            raise NotFoundError(f"User (id={user_id}) not found.")

        return FollowDao().find_following(user_id)
    
    @log
    def get_followers(self, user_id: int) -> list[User]:
        """Retrieves the users who follow a given user.
        Args:
            user_id (int): id of the user whose followers are requested
        Returns:
            list[User] following user_id (empty list if nobody follows them)
        Raises:
            NotFoundError: if user_id does not match any user
        """
        if UserService().find_by_id(user_id) is None:
            raise NotFoundError(f"User (id={user_id}) not found.")

        return FollowDao().find_followers(user_id)