"""HTTP endpoints for the review and reaction vertical."""

from contextlib import contextmanager

from fastapi import APIRouter, Depends, HTTPException, Response

from business_object.review import Review
from business_object.user import User
from controller.dependencies import get_current_user
from schema.book_model import BookModel
from schema.like_model import LikeCountModel, LikeModel, LikeReadModel
from schema.review_model import ReviewCreateModel, ReviewReadModel
from service.like_service import LikeService
from service.review_service import ReviewService
from utils.exceptions import ConflictError, ForbiddenError, NotFoundError

router = APIRouter()


def get_review_service() -> ReviewService:
    """Dependency provider, replaceable by a mock in endpoint tests."""
    return ReviewService()


def get_like_service() -> LikeService:
    """Dependency provider for reactions and their counters."""
    return LikeService()


@contextmanager
def _http_errors():
    """Translate only known business errors; unexpected errors remain HTTP 500."""
    try:
        yield
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ForbiddenError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _to_model(review: Review, like_service: LikeService) -> ReviewReadModel:
    """Flatten nested objects and add reaction counts for the public response."""
    likes, dislikes = like_service.count(review.review_id)
    book = review.reading.book
    return ReviewReadModel(
        review_id=review.review_id,
        reading_id=review.reading.reading_id,
        user_id=review.reading.user.user_id,
        username=review.reading.user.username,
        book=BookModel(
            book_id=book.book_id,
            work_id=book.work_id,
            title=book.title,
            authors=book.authors,
            cover_url=book.cover_url,
        ),
        text=review.text,
        publication_date=review.publication_date,
        likes=likes,
        dislikes=dislikes,
    )


@router.post(
    "/readings/{reading_id}/review",
    response_model=ReviewReadModel,
    status_code=201,
    tags=["Reviews"],
)
def write_review(
    reading_id: int,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """Write the authenticated user's review of a completed/abandoned reading."""
    with _http_errors():
        review = review_service.write_review(current_user, reading_id, review_data.text)
        return _to_model(review, like_service)


@router.get("/readings/{reading_id}/review", response_model=ReviewReadModel, tags=["Reviews"])
def review_of_reading(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """Return the review attached to a reading."""
    with _http_errors():
        review = review_service.get_by_reading(reading_id)
        if review is None:
            raise NotFoundError("No review for this reading.")
        return _to_model(review, like_service)


@router.get("/reviews/{review_id}", response_model=ReviewReadModel, tags=["Reviews"])
def review_by_id(
    review_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """Return a review by its identifier."""
    with _http_errors():
        review = review_service.find_by_id(review_id)
        if review is None:
            raise NotFoundError(f"Review (id={review_id}) not found.")
        return _to_model(review, like_service)


@router.put("/reviews/{review_id}", response_model=ReviewReadModel, tags=["Reviews"])
def update_review(
    review_id: int,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """Edit a review's text; only its author may do so."""
    with _http_errors():
        review = review_service.update_review(current_user, review_id, review_data.text)
        return _to_model(review, like_service)


@router.delete("/reviews/{review_id}", status_code=204, tags=["Reviews"])
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
):
    """Delete the authenticated user's review and its reactions."""
    with _http_errors():
        review_service.delete_review(current_user, review_id)
    return Response(status_code=204)


@router.get("/users/{user_id}/reviews", response_model=list[ReviewReadModel], tags=["Reviews"])
def reviews_of_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """List an author's reviews, or an empty list."""
    with _http_errors():
        return [_to_model(review, like_service) for review in review_service.get_by_user(user_id)]


@router.get("/books/{work_id}/reviews", response_model=list[ReviewReadModel], tags=["Reviews"])
def reviews_of_book(
    work_id: str,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    like_service: LikeService = Depends(get_like_service),
):
    """List reviews using an Open Library work ID, such as OL10263W."""
    with _http_errors():
        return [_to_model(review, like_service) for review in review_service.get_by_book(work_id)]


@router.put("/reviews/{review_id}/like", response_model=LikeReadModel, tags=["Likes"])
def react(
    review_id: int,
    like_data: LikeModel,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service),
):
    """Create or replace the authenticated user's reaction."""
    with _http_errors():
        reaction = like_service.react(current_user, review_id, like_data.liked)
    return LikeReadModel(
        review_id=reaction.review.review_id,
        user_id=reaction.user.user_id,
        liked=reaction.liked,
        like_date=reaction.like_date,
    )


@router.delete("/reviews/{review_id}/like", status_code=204, tags=["Likes"])
def remove_reaction(
    review_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service),
):
    """Remove the authenticated user's reaction, or return 404."""
    with _http_errors():
        like_service.remove_reaction(current_user, review_id)
    return Response(status_code=204)


@router.get("/reviews/{review_id}/likes", response_model=LikeCountModel, tags=["Likes"])
def like_count(
    review_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service),
):
    """Return separate totals for likes and dislikes."""
    with _http_errors():
        likes, dislikes = like_service.count(review_id)
    return LikeCountModel(likes=likes, dislikes=dislikes)
