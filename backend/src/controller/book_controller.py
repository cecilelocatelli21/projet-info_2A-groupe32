# controller/book_controller.py


from fastapi import APIRouter, Depends, HTTPException

from schema.book_model import BookModel
from service.book_service import BookService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_book_service():
    """Dependency Injection provider for UserService."""
    return BookService()


@router.get("/", response_model=list[BookModel], tags=["Book"])
async def find_all(book_service=Depends(get_book_service)):
    """List all books.
    Returns:
        list[BookModel]: A list of all registered books.
    """
    logger.info("List all books")
    books_list = book_service.find_all()
    return books_list


@router.get("/{work_id}", response_model=BookModel, tags=["Book"])
async def find_by_work_id(work_id: str, book_service=Depends(get_book_service)):
    """Find a book by its ID used in OpenLibrary.
    Args:
        work_id (str)
        book_service (BookService): The service used to interact with user data
    Returns:
        BookModel: The book data if found
    Raises:
        HTTPException: 404 error if the book is not found
    """
    logger.info("Find a book by Work id (OpenLibrary data)")
    book = book_service.find_by_work_id(work_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book (id={work_id}) not found.")
    return book


@router.get("/{book_id}", response_model=BookModel, tags=["Book"])
async def find_by_id(book_id: int, book_service=Depends(get_book_service)):
    """Find a book by its ID used in our local database.
    Args:
        book_id (int)
        book_service (BookService): The service used to interact with user data
    Returns:
        BookModel: The book data if found
    Raises:
        HTTPException: 404 error if the book is not found
    """
    logger.info("Find a book by Work id (OpenLibrary data)")
    book = book_service.find_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book (id={book_id}) not found.")
    return book
