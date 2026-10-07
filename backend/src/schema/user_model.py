import os

from pydantic import BaseModel, EmailStr, Field, field_validator

USERNAME_MAX_LENGTH = 30  
PASSWORD_MAX_LENGTH = 128
BIO_MAX_LENGTH = 1000


def _check_password_length(password: str) -> str:
    """Shared rule for every model that receives a new password."""
    min_len = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    if len(password) < min_len:
        raise ValueError(f"Password must be at least {min_len} characters long")
    return password


class UserModel(BaseModel):
    """Body of POST /users (account creation). No user_id: the database gives it."""

    username: str = Field(min_length=2, max_length=USERNAME_MAX_LENGTH)
    email: EmailStr
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        if v != v.strip():
            raise ValueError("Username must not start or end with a space")
        return v

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        return _check_password_length(v)


# Ce que le user aura à saisir pour obtenir des informations
class UserReadModel(BaseModel):
    user_id: int
    username: str
    bio: str | None
    email: EmailStr


# Ce dont le user aura besoin pour s'identifier
class UserLoginModel(BaseModel):
    """Body of POST /login"""
    username: str
    password: str


class UserUpdateModel(BaseModel):
    """Body of PUT /users/{user_id}. A field left to None is not changed."""

    bio: str | None = Field(default=None, max_length=BIO_MAX_LENGTH)
    email: EmailStr | None = None


# Public view of a user: never exposes email, password or token
class UserPublicModel(BaseModel):
    user_id: int
    username: str
    bio: str | None


class PasswordChangeModel(BaseModel):
    """Body of PUT /users/{user_id}/password."""

    old_password: str
    new_password: str = Field(max_length=PASSWORD_MAX_LENGTH)

    @field_validator("new_password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        return _check_password_length(v)


class TokenModel(BaseModel):
    """Response of POST /login. user_id lets the client call /users/{user_id}."""

    user_id: int
    access_token: str
    token_type: str = "bearer"