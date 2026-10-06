from pydantic import BaseModel


class BookModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange player information,
    ensuring data consistency and validation during API requests and responses."""

    book_id: int | None
    work_id: str | None
    title: str | None
    authors: str | None
    cover_url: str | None

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
