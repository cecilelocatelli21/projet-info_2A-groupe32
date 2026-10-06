import requests

from business_object.book import Book
from utils.log_utils import get_logger, log
from utils.singleton import Singleton


class OpenLibraryError(Exception):
    """OpenLibrary unjoignable, timeout or unexpected response"""
    ...

class OpenLibraryClient(metaclass=Singleton):
    BASE_URL = "https://openlibrary.org"

    @log
    def get_work(self, work_id: str) -> Book or None:
        """get a work in OpenLibrary if it exists
        """
        ...