import secrets

from business_object.user import User
from dao.user_dao import UserDao
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError
from utils.log_utils import log
from utils.security import hash_password


class UserService:
    """Service that handles business logic related to users (creation, search, etc.)."""

    @log
    def create_account(self, username: str, email: str, password: str) -> User:
        """Creates a new account in the system.
        Args:
            username (str)
            password (str) will be hashed before storage
            email (str)
        Returns:
            user created or None if creation failed.
         """
        if UserDao().find_by_username(username) is not None:
            raise ConflictError(f"Username '{username}' is already taken.")
        if UserDao().find_by_email(email) is not None:
            raise ConflictError(f"Email '{email}' is already used.")

        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password, username),
        )
        return new_user if UserDao().create(new_user) else None

    @log
    def login(self, username: str, password: str) -> User | None:
        """Authenticates a user using their credentials.
        Args:
            username (str)
            password (str)
        Returns:
            User object if authentication is successful, otherwise None.
         """
        user = UserDao().find_by_username(username)
        if user is None or not secrets.compare_digest(
            user.password_hash, hash_password(password, username)
        ):
            return None
        # Generate a token and update the User
        user.access_token = secrets.token_urlsafe(32)
        UserDao().update(user)
        return user

    @log
    def logout(self, user: User) -> bool:
        user.access_token = None
        return UserDao().update(user)

    @log
    def update(self, user) -> User:
         """Updates an existing user's information.
         Args:
             User object containing updated information.
         Returns:
             The updated User object, or None if the update failed.
         """
         return user if UserDao().update(user) else None

    @log
    def username_already_used(self, username: str) -> bool:
         """Check if a username is already used.
         Args:
             username (str)
         Returns:
             True if the username already exists in the database.
         """
         user = UserDao().find_all()
         return username in [p.username for p in user]


    def find_by_token(self, token: str) -> User | None:
        """Not decorated with @log so that tokens never end up in the logs."""
        return UserDao().find_by_token(token)

    @log
    def find_by_id(self, user_id: int) -> User | None:
        """Finds a specific user by their unique id."""
        return UserDao().find_by_id(user_id)

    def _get_own_account(self, current_user: User, user_id: int) -> User:
        """Checks that user_id exists and is the current user's account.
        Existence is checked first, so an unknown id gives 404 rather than 403.
        """
        user = self.get_by_id(user_id)
        if current_user.user_id != user.user_id:
            raise ForbiddenError("You can only modify your own account.")
        return user

    @log
    def change_password(self, current_user: User, user_id: int, old_password: str, new_password: str) -> bool:
        """ Change password after cheking the former password"""
        user = self._get_own_account(current_user, user_id)

        if not secrets.compare_digest(user.password_hash, hash_password(old_password, user.username)):
            raise ValueError("Old password is incorrect.")

        user.password_hash = hash_password(new_password, user.username)
        return UserDao().update(user)

    @log
    def delete_account(self, current_user: User, user_id: int) -> bool:
        user = self._get_own_account(current_user, user_id)
        return UserDao().delete(user.user_id)
