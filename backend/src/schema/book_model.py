import os

from pydantic import BaseModel, EmailStr, field_validator


class BookModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange player information,
    ensuring data consistency and validation during API requests and responses."""

    book_id: int | None = None
    work_id: str
    title: str
    authors: str
    cover_url: str

    # @field_validator("password")
    # @classmethod
    # def check_password_length(cls, v: str) -> str:
    #     min_len = int(os.environ["PASSWORD_MIN_LENGTH"])
    #     if len(v) < min_len:
    #         raise ValueError(f"Password must be at least {min_len} characters long")
    #     return v


# class PlayerReadModel(BaseModel):
#     id_player: int
#     username: str
#     elo: int | None
#     email: EmailStr
#     pokemon_fan: bool | None


# class PlayerLoginModel(BaseModel):
#     username: str
#     password: str
