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

        user.access_token = secrets.token_urlsafe(32)
        UserDao().update(user)
        return user

    @log
    def logout(self, user: User) -> bool:
        user.access_token = None
        return UserDao().update(user)

    def find_by_token(self, token: str) -> User | None:
        """Not decorated with @log so that tokens never end up in the logs."""
        return UserDao().find_by_token(token)
    # @log
    # def create(self, username, password, elo, email, pokemon_fan) -> Player:
    #     """Creates a new player in the system.
    #     Args:
    #         username (str)
    #         password (str) will be hashed before storage
    #         elo (int)
    #         email (str)
    #         pokemon_fan (bool)
    #     Returns:
    #         Player object created or None if creation failed.
    #     """
    #     new_player = Player(
    #         username=username,
    #         password=hash_password(password, username),
    #         elo=elo,
    #         email=email,
    #         pokemon_fan=pokemon_fan,
    #     )
    #     return new_player if PlayerDao().create(new_player) else None


    # @log
    # def update(self, player) -> Player:
    #     """Updates an existing player's information.
    #     Args:
    #         Player object containing updated information.
    #     Returns:
    #         The updated Player object, or None if the update failed.
    #     """
    #     return player if PlayerDao().update(player) else None

    # @log
    # def delete(self, player) -> bool:
    #     """Delete a player account.
    #     Args:
    #         Player object to be deleted.
    #     Returns:
    #         True if deletion was successful, False otherwise.
    #     """
    #     return PlayerDao().delete(player)

    # @log
    # def login(self, username: str, password: str) -> Player:
    #     """Authenticates a player using their credentials.
    #     Args:
    #         username (str)
    #         password (str)
    #     Returns:
    #         Player object if authentication is successful, otherwise None.
    #     """
    #     player = PlayerDao().login(username, hash_password(password, username))
    #     if player:
    #         # Generate a token and update the Player
    #         player.access_token = secrets.token_urlsafe(32)
    #         self.update(player)
    #         return player
    #     return None

    # @log
    # def username_already_used(self, username: str) -> bool:
    #     """Check if a username is already used.
    #     Args:
    #         username (str)
    #     Returns:
    #         True if the username already exists in the database.
    #     """
    #     players = PlayerDao().find_all()
    #     return username in [p.username for p in players]
