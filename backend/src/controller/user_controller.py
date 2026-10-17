"""Routes of the User vertical: account creation, profiles, search and account changes.

Access levels (see "Ex-Libris — Endpoints de l'API"):
    - without token: POST /users
    - logged in (valid token): GET /users/me, GET /users, GET /users/{user_id}
    - owner only ("titulaire"): PUT /users/{user_id}, PUT /users/{user_id}/password,
      DELETE /users/{user_id}

The controller holds no business rule: it calls UserService, converts the User
business objects into Pydantic models and turns the service's exceptions into
HTTP status codes.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from business_object.user import User
from controller.dependencies import get_current_user
from schema.user_model import (
    PasswordChangeModel,
    UserModel,
    UserPublicModel,
    UserReadModel,
    UserUpdateModel,
)
from service.user_service import UserService
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)

# --------- Modèle des return selon si l'utilisateur connecté consulte son profil ou celui d'un autre utilisateur --------


def get_user_service():
    """Dependency Injection provider for UserService.

    Returns:
        UserService: the service used by every route of this file
    """
    return UserService()


def _to_read_model(u: User) -> UserReadModel:
    """Converts a User into its private view, with the email. Only used for responses sent to the user themselves.

    Args:
        user (User): business object returned by the service
    Returns:
        UserReadModel: user_id, username, bio and email (never password_hash nor access_token)
    """
    return UserReadModel(user_id=u.user_id, username=u.username, bio=u.bio, email=u.email)


def _to_public_model(u: User) -> UserPublicModel:
    """Converts a User into its public view, without the email. Used for every response that other users can see.
    Args:
        user (User): business object returned by the service
    Returns:
        UserPublicModel: user_id, username and bio
    """
    return UserPublicModel(user_id=u.user_id, username=u.username, bio=u.bio)


# -------- Pour un utilisateur non connecté encore -----------


@router.post("/users", response_model=UserReadModel, status_code=status.HTTP_201_CREATED)
def create_user(u: UserModel, user_service=Depends(get_user_service)):
    """Create a new user.
    Args:
        u (UserModel): The player data to create.
        user_service (UserService): The service used to interact with player data.
    Returns:
        UserReadModel: The newly created user data.
    Raises:
        HTTPException: 400 error if the username is already taken.
        HTTPException: 500 error if the creation process fails.
    """
    logger.info("Create user")
    try:
        user = user_service.create_account(
            username=u.username,
            email=u.email,
            password=u.password,
        )
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return _to_read_model(user)


# -------Pour un utilisateur connecté--------------


@router.get("/", response_model=list[UserReadModel], tags=["Users"])
async def find_all_users(user_service=Depends(get_user_service)):
    """List all users.
    Returns:
        list[UserReadModel]: A list of all registered users.
    """
    logger.info("List all users")
    users_list = user_service.find_all()
    return users_list


@router.get("/users", response_model=list[UserPublicModel])
def search_users(
    username: str = "", user_service=Depends(get_user_service), _: User = Depends(get_current_user)
):
    """Searches users whose username contains `username` (case insensitive).

    Args:
        username (str): part of a username, given as ?username=...;
            empty returns every user
        user_service (UserService): injected service
        _ (User): logged-in user, unused here but required to call the route
    Returns:
        list[UserPublicModel]: matching users sorted by username, without emails
    Raises:
        HTTPException: 401 if the token is missing or invalid
    """
    logger.info("Search users")
    return [_to_public_model(u) for u in user_service.search(username)]


@router.get("/users/{user_id}", response_model=UserPublicModel)
def user_by_id(
    user_id: int, user_service=Depends(get_user_service), _: User = Depends(get_current_user)
):
    """Returns the public profile of a user (no email).
    Args:
        user_id (int): id of the user to display
        user_service (UserService): injected service
        _ (User): logged-in user, unused here but required to call the route
    Returns:
        UserPublicModel: the user's public view
    Raises:
        HTTPException: 401 if the token is missing or invalid
        HTTPException: 404 if the user does not exist
    """
    logger.info("Find a user by id")
    user = user_service.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User (id={user_id}) not found.")
    return _to_public_model(user)


# ------Pour le titulaire du compte----------

# changer bio ou email


@router.put("/users/{user_id}", response_model=UserReadModel)
def update_user(
    user_id: int,
    changes: UserUpdateModel,
    current_user: User = Depends(get_current_user),
    user_service=Depends(get_user_service),
):
    """Changes the bio and/or the email of one's own account.
    A field left out of the body (None) is not changed.
    Args:
        user_id (int): id of the account to modify, must be the logged-in user's
        changes (UserUpdateModel): new bio and/or new email
        current_user (User): user found from the token by get_current_user
        user_service (UserService): injected service
    Returns:
        UserReadModel: the updated account
    Raises:
        HTTPException: 401 if the token is missing or invalid
        HTTPException: 403 if user_id is not the logged-in user's account
        HTTPException: 404 if the user does not exist
        HTTPException: 409 if the new email is already used by another account
    """
    logger.info("Update user")
    try:
        user = user_service.update_profile(
            current_user, user_id, bio=changes.bio, email=changes.email
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return _to_read_model(user)


# Changer mdp


@router.put("/users/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    user_id: int,
    passwords: PasswordChangeModel,
    current_user: User = Depends(get_current_user),
    user_service=Depends(get_user_service),
):
    """Changes the password of one's own account.

    Args:
        user_id (int): id of the account to modify, must be the logged-in user's
        passwords (PasswordChangeModel): old password (checked) and new password
            (length validated by Pydantic)
        current_user (User): user found from the token by get_current_user
        user_service (UserService): injected service
    Returns:
        Response: empty response (HTTP 204)
    Raises:
        HTTPException: 400 if the old password is wrong
        HTTPException: 401 if the token is missing or invalid
        HTTPException: 403 if user_id is not the logged-in user's account
        HTTPException: 404 if the user does not exist
    """
    logger.info("Change password")
    try:
        user_service.change_password(
            current_user, user_id, passwords.old_password, passwords.new_password
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# supprimer un user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service=Depends(get_user_service),
):
    """Deletes one's own account.

    Readings, reviews, likes and follows of the user are deleted with it
    (ON DELETE CASCADE in init_db.sql).

    Args:
        user_id (int): id of the account to delete, must be the logged-in user's
        current_user (User): user found from the token by get_current_user
        user_service (UserService): injected service
    Returns:
        Response: empty response (HTTP 204)
    Raises:
        HTTPException: 401 if the token is missing or invalid
        HTTPException: 403 if user_id is not the logged-in user's account
        HTTPException: 404 if the user does not exist
    """
    logger.info("Delete user")
    try:
        user_service.delete_account(current_user, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)
