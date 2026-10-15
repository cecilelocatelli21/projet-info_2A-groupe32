from datetime import datetime

from pydantic import BaseModel


class BookModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange player information,
    ensuring data consistency and validation during API requests and responses."""

    book_id: int
    work_id: str
    title: str
    authors: str
    cover_url: str | None = None


class BookSearchResultModel(BaseModel):
    """For the research in OpenLibrary database"""

    work_id: str
    title: str
    authors: str
    cover_url: str | None = None


class EditionModel(BaseModel):
    """One specific edition associated with work"""

    title: str | None = None
    publisher: str | None = None
    publish_date: datetime | None = None
    number_of_pages: int | None = None
    isbn: str | None = None


class BookDetailModel(BaseModel):
    """A book with all necessary details"""

    work_id: str
    book_id: int | None = None
    title: str
    authors: str | None = None
    cover_url: str | None = None
    subjects: list[str] = []
    description: str | None = None
    editions: list[EditionModel] = []
    average_rating: float | None = None

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
