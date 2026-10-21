import secrets

from business_object.user import User
from dao.user_dao import UserDao
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError
from utils.log_utils import log
from utils.security import hash_password


class UserService:
    """Business logic of the User vertical: accounts, authentication, profiles and search.

    Methods that modify an account receive the logged-in user (current_user,
    found from the token by get_current_user) and check through
    _get_own_account that the targeted account is their own.
    """

    # ---------- Account creation (public) ----------
    @log
    def create_account(self, username: str, email: str, password: str) -> User | None:
        """Creates a new account in the system.
        Args:
            username (str): chosen username, must not be already taken
            email (str): email address, must not be already used
            password (str): password in plain text, never stored as is
        Returns:
            User if user created, otherwise None.
        Raises:
            ConflictError: if the username or the email is already used
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
    def username_already_used(self, username: str) -> bool:
        """Check if a username is already used.

        Not used by create_account, which calls find_by_username directly.

        Args:
            (str): username to check
        Returns:
            True if the username already exists in the database.
        """
        user = UserDao().find_all()
        return username in [p.username for p in user]

    # ---------- Authentication ----------

    @log
    def login(self, username: str, password: str) -> User | None:
        """Authenticates a user using their credentials.

        The token is saved in the database (access_token column) and replaces
        any previous one.

        Args:
            username (str) : username of the account
            password (str) : password in plain text
        Returns:
            User object with the new access_token if authentication is successful, otherwise None.
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
        """Logs a user out, the token is removed from the database.

        Args:
            user (User): the logged-in user, given by get_current_user
        Returns:
            bool: True if the database was updated
        """
        user.access_token = None
        return UserDao().update(user)

    def find_by_token(self, token: str) -> User | None:
        """Finds the user who owns a token. Used by get_current_user.

        Not decorated with @log so that tokens never end up in the logs.

        Args:
            token (str): access token sent in the Authorization header
        Returns:
            User | None: the user, or None if the token is unknown
        """
        return UserDao().find_by_token(token)

    # ---------- Consultation (logged-in user) ----------

    @log
    def find_by_id(self, user_id: int) -> User | None:
        """Finds a specific user by their unique id.

        Args:
            user_id (int): id of the user
        Returns:
            User | None: the user, or None if no user has this id
        """
        return UserDao().find_by_id(user_id)

    @log
    def search(self, pattern: str) -> list[User]:
        """Searches users whose username contains a pattern (case insensitive).

        Args:
            pattern (str): part of a username; an empty string returns every user
        Returns:
            list[User]: matching users sorted by username (empty if none)
        """

        return UserDao().search_by_username(pattern)

    # ---------- Changes to one's own account (owner only) ----------

    def _get_own_account(self, current_user: User, user_id: int) -> User:
        """Checks that user_id exists and is the current user's account.

        Existence is checked first, so an unknown id gives 404 rather than 403.

        Args:
            curent_user (User): the logged-in user, given by get_current_user
            user_id (int): id of the targeted account
        Return:
            User: the targeted account, read from the database
        Raises:
            NotFoundError: if no user has this user_id
            ForbiddenError: if user_id is not current_user's account
        """
        user = self.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found.")
        if current_user.user_id != user.user_id:
            raise ForbiddenError("You can only modify your own account.")
        return user

    @log
    def update_profile(self, current_user: User, user_id: int, bio: str | None = None,
                       email: str | None = None) -> User:
        """Updates the bio and/or the email of the logged-in user's own account.
 
        A field left to None is not changed.

        Args:
            curent_user (User): the logged-in user, given by get_current_user
            user_id (int): id of the account to modify, must be current_user's
            bio (str | None): new bio
            email (str | None): new email, must not be already used by another account
        Returns:
            The updated User object, or None if the update failed.
        Raises:
            NotFoundError: if no user has this user_id
            ForbiddenError: if user_id is not current_user's account
            ConflictError: if the new email is already used by another account
        """
        user = self._get_own_account(current_user, user_id)
        if bio is not None:
            user.bio = bio
        if email is not None and email != user.email:
            other = UserDao().find_by_email(email)
            if other is not None:
                raise ConflictError(f"Email '{email}' is already used.")
            user.email = email
        return user if UserDao().update(user) else None

    @log
    def change_password(
        self, current_user: User, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """Changes the password of the logged-in user's own account.
 
        The old password is checked before the new one is hashed and saved.
 
        Args:
            current_user (User): the logged-in user, given by get_current_user
            user_id (int): id of the account to modify, must be current_user's
            old_password (str): current password in plain text
            new_password (str): new password in plain text
        Returns:
            bool: True if the database was updated
        Raises:
            NotFoundError: if no user has this user_id
            ForbiddenError: if user_id is not current_user's account
            ValueError: if old_password is wrong
        """
        user = self._get_own_account(current_user, user_id)

        if not secrets.compare_digest(
            user.password_hash, hash_password(old_password, user.username)
        ):
            raise ValueError("Old password is incorrect.")

        user.password_hash = hash_password(new_password, user.username)
        return UserDao().update(user)

    @log
    def delete_account(self, current_user: User, user_id: int) -> bool:
        """Deletes the logged-in user's own account.
 
        Their readings, reviews, likes and follows are deleted with it
        (ON DELETE CASCADE in the database).
 
        Args:
            current_user (User): the logged-in user, given by get_current_user
            user_id (int): id of the account to delete, must be current_user's
        Returns:
            bool: True if the account was deleted
        Raises:
            NotFoundError: if no user has this user_id
            ForbiddenError: if user_id is not current_user's account
        """
        user = self._get_own_account(current_user, user_id)
        return UserDao().delete(user.user_id)

