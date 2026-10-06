from datetime import date
from typing import Literal

from pydantic import BaseModel, Field
from schema.book_model import BookModel

ReadingStatus = Literal[
    "to read",
    "in progress",
    "read",
    "abandoned"
]


class ReadingCreateModel(BaseModel):
    work_id: str
    status: ReadingStatus = "to read"


class ReadingUpdateModel(BaseModel):
    status: ReadingStatus | None = None
    rating: int | None = Field(
        default=None,
        ge=0,
        le=5
    )
    date_read: date | None = None


class ReadingReadModel(BaseModel):
    reading_id: int
    user_id: int
    book: BookModel
    status: ReadingStatus
    date_added: date
    date_read: date | None
    rating: int | None
