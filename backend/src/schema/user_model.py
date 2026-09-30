import os

from pydantic import BaseModel, EmailStr, field_validator


class UserModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange user information,
    ensuring data consistency and validation during API requests and responses."""

    user_id: int | None = None
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        min_len = int(os.environ["PASSWORD_MIN_LENGTH"])
        if len(v) < min_len:
            raise ValueError(f"Password must be at least {min_len} characters long")
        return v

# Ce que le user aura à saisir pour obtenir des informations
class UserReadModel(BaseModel):
    user_id: int
    username: str
    bio: str | None
    email: EmailStr

# Ce dont le user aura besoin pour s'identifier
class UserLoginModel(BaseModel):
    username: str
    password: str

# Public view of a user: never exposes email, password or token
class UserPublicModel(BaseModel):
    user_id: int
    username: str
    bio: str | None