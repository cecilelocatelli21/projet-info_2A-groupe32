"""Public request and response contracts for reviews."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from schema.book_model import BookModel


class ReviewCreateModel(BaseModel):
    """A review's editable content; identity comes from authentication."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    text: str = Field(min_length=1)


class ReviewReadModel(BaseModel):
    """Public review, without the author's email, password or access token."""

    review_id: int
    reading_id: int
    user_id: int
    username: str
    book: BookModel
    text: str
    publication_date: date
    likes: int
    dislikes: int
