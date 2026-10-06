from controller.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Response, status
from schema.book_model import BookModel

from business_object.reading import Reading
from business_object.user import User
from schema.reading_model import (
    ReadingCreateModel,
    ReadingReadModel,
    ReadingUpdateModel,
)
from service.reading_service import ReadingService
from utils.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_reading_service():
    """Dependency Injection provider for ReadingService."""
    return ReadingService()


def _to_model(reading: Reading) -> ReadingReadModel:
    """Convert a Reading business object to a ReadingReadModel."""
    return ReadingReadModel(
        reading_id=reading.reading_id,
        user_id=reading.user.user_id,
        book=BookModel(
            book_id=reading.book.book_id,
            work_id=reading.book.work_id,
            title=reading.book.title,
            authors=reading.book.authors,
            cover_url=reading.book.cover_url,
        ),
        status=reading.status,
        date_added=reading.date_added,
        date_read=reading.date_read,
        rating=reading.rating,
    )


@router.post(
    "/readings",
    response_model=ReadingReadModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Readings"],
)
async def add_reading(
    reading_data: ReadingCreateModel,
    current_user: User = Depends(get_current_user),
    reading_service: ReadingService = Depends(get_reading_service),
):
    """Add a book to the current user's library."""
    logger.info(
        "Add book work_id=%s to user_id=%s library",
        reading_data.work_id,
        current_user.user_id,
    )

    try:
        reading = reading_service.add_book(
            user=current_user,
            work_id=reading_data.work_id,
            status=reading_data.status,
        )

        return _to_model(reading)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get(
    "/readings/{reading_id}",
    response_model=ReadingReadModel,
    tags=["Readings"],
)
async def get_reading(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    reading_service: ReadingService = Depends(get_reading_service),
):
    """Get a reading by its identifier."""
    logger.info(
        "Get reading_id=%s by user_id=%s",
        reading_id,
        current_user.user_id,
    )

    reading = reading_service.find_by_id(reading_id)

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail=f"Reading (id={reading_id}) not found.",
        )

    return _to_model(reading)


@router.get(
    "/users/{user_id}/readings",
    response_model=list[ReadingReadModel],
    tags=["Readings"],
)
async def get_library(
    user_id: int,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    reading_service: ReadingService = Depends(get_reading_service),
):
    """Get a user's library, optionally filtered by status."""
    logger.info(
        "Get library of user_id=%s by user_id=%s",
        user_id,
        current_user.user_id,
    )

    readings = reading_service.get_library(
        user_id=user_id,
        status=status,
    )

    return [_to_model(reading) for reading in readings]


@router.patch(
    "/readings/{reading_id}",
    response_model=ReadingReadModel,
    tags=["Readings"],
)
async def update_reading(
    reading_id: int,
    reading_data: ReadingUpdateModel,
    current_user: User = Depends(get_current_user),
    reading_service: ReadingService = Depends(get_reading_service),
):
    """Update a reading belonging to the current user."""
    logger.info(
        "Update reading_id=%s by user_id=%s",
        reading_id,
        current_user.user_id,
    )

    try:
        reading = reading_service.update_reading(
            user=current_user,
            reading_id=reading_id,
            status=reading_data.status,
            rating=reading_data.rating,
            date_read=reading_data.date_read,
        )

        return _to_model(reading)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/readings/{reading_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Readings"],
)
async def delete_reading(
    reading_id: int,
    current_user: User = Depends(get_current_user),
    reading_service: ReadingService = Depends(get_reading_service),
):
    """Remove a reading from the current user's library."""
    logger.info(
        "Delete reading_id=%s by user_id=%s",
        reading_id,
        current_user.user_id,
    )

    try:
        reading_service.delete_reading(
            user=current_user,
            reading_id=reading_id,
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))