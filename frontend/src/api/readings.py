"""Library routes (vertical Reading).

Endpoints used:
    POST /readings
    GET /users/{user_id}/readings?status=
    PATCH /readings/{reading_id}
    DELETE /readings/{reading_id}
"""

from utils.api_client import api_client


def add_reading(work_id: str, status: str = "to read") -> dict:
    """Adds a book to the connected user's library (201).
    404 book not found, 409 already in the library, 503 OpenLibrary unreachable."""
    return api_client.post("/readings", json={"work_id": work_id, "status": status})


def get_library(user_id: int, status: str | None = None) -> dict:
    """Library of a user (list[ReadingReadModel]), optionally filtered by status."""
    params = {"status": status} if status else None
    return api_client.get(f"/users/{user_id}/readings", params=params)


def update_reading(reading_id: int, **fields) -> dict:
    """Updates a reading of the connected user; only the given fields are sent
    (status, rating, date_read). 400 rule not respected, 403 not the owner, 404 unknown."""
    return api_client.patch(f"/readings/{reading_id}", json=fields)


def delete_reading(reading_id: int) -> dict:
    """Removes a book from the connected user's library (204)."""
    return api_client.delete(f"/readings/{reading_id}")
