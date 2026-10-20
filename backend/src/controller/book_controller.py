# controller/book_controller.py


from fastapi import APIRouter, Depends, HTTPException, Query

from controller.dependencies import get_current_user
from schema.book_model import BookDetailModel, BookModel, BookSearchResultModel, PopularBookModel
from service.book_service import BookService
from service.user_service import User
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_book_service():
    """Dependency Injection provider for BookService."""
    return BookService()


@router.get("/find_all/", response_model=list[BookModel], tags=["Books"])
async def find_all(book_service=Depends(get_book_service)):
    """List all books.
    Returns:
        list[BookModel]: A list of all registered books.
    """
    logger.info("List all books")
    books_list = book_service.find_all()
    return books_list


@router.get("/work/{work_id}", response_model=BookModel, tags=["Books"])
async def find_by_work_id(work_id: str,
current_user=Depends(get_current_user),
book_service=Depends(get_book_service)):
    """Find a book by its ID used in OpenLibrary.
    Args:
        work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        book_service (BookService): The service used to interact with user data
    Returns:
        BookModel: The book data if found
    Raises:
        HTTPException: 404 error if the book is not found
    """
    logger.info("Find a book by Work id (OpenLibrary data)")
    book = book_service.find_by_work_id(work_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book (work_id={work_id}) not found.")
    return book


@router.get("/id/{book_id}", response_model=BookModel, tags=["Books"])
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
    logger.info("Find a book by Book id (local database data)")
    book = book_service.find_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book (book_id={book_id}) not found.")
    return book


@router.get("/", response_model=list[BookSearchResultModel], tags=["Books"])
async def search_books(q: str,
current_user: User = Depends(get_current_user),
book_service=Depends(get_book_service)):
    """Search books in OpenLibrary

        Args:
            q (str): query typed by the user to search books in OpenLibrary (for instance: "le petit prince")
            current_user (User): the current user who is doing this research
            book_service (BookService): The service used to interact with user data
        Returns:
            A list of books corresponding to the response given by OpenLibrary
    """
    logger.info("Execute a research into OpenLibrary (function search_books)")
    books = book_service.search(query=q)
    if books == []:
        raise HTTPException(status_code=404, detail="The request gave no answer in OpenLibrary client.")

    return books

@router.get("/{work_id}", response_model=BookDetailModel, tags=["Books"])
async def get_book(work_id: str,
current_user: User = Depends(get_current_user),
book_service=Depends(get_book_service)) -> dict:
    """Search books in OpenLibrary and send more details for this book that what our local database contains

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
            current_user (User): the current user who is doing this research
            book_service (BookService): The service used to interact with user data
        Returns:
            A dictionnary containing all details for the target book.
    """

    logger.info("Execute a research into OpenLibrary to get details for a book (function get_book)")
    book_details = book_service.get_book_details(work_id)
    if book_details is None:
        raise HTTPException(status_code=404, detail="The work id has not been found in OpenLibrary.")

    return book_details


@router.get(
    "/recommendations",
    response_model=list[PopularBookModel],
    tags=["Books"],
)
async def get_popular_books(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    book_service=Depends(get_book_service),
) -> list[PopularBookModel]:
    """
    Retrieve popular book recommendations for the authenticated user.

    Popular books are ranked by their average rating, number of ratings,
    and title. Books already present in the user's library are excluded.

    Args:
        limit (int): Maximum number of books to return.
            Defaults to 10. Must be between 1 and 50.
        current_user (User): Authenticated user obtained from the access token.
        book_service: Service responsible for retrieving popular books.

    Returns:
        list[PopularBookModel]: A list of popular books. Each book contains
        its ID, Open Library work ID, title, authors, cover URL,
        average rating, and number of ratings. Returns an empty list
        if no recommendations are available.
    """
    logger.info("Get popular book recommendations")

    books = book_service.get_popular_books(
        user_id=current_user.user_id,
        limit=limit,
    )

    return books
