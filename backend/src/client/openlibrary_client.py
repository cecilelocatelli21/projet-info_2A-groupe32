import json

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
    def search(self, query: str, limit: int = 20) -> list[Book]:
        """search books in open library
        """
        ...

    @log
    def get_work(self, work_id: str) -> Book or None:
        """get a work in OpenLibrary if it exists
        """
        r = requests.get(url= f"{self.BASE_URL}/works/{work_id}.json")
        if r.status_code != 200:
            raise Exception(f"Cannot reach (HTTP {r.status_code}): {r.text}")
        else:
            raw_json = r.json()
            # print(json.dumps(raw_json, indent=2))  # Pretty print

        if "error" in raw_json:
            return None

        title = raw_json["title"]

        authors_in_work = raw_json["authors"]
        author_key = authors_in_work[0]["author"]["key"].split("/")[2]
        authors = self._get_author_name(author_key=author_key)

        #cover_in_work = raw_json["covers"]
        cover_url = "https://covers.openlibrary.org/b/ID/" + str(raw_json["covers"][-1]) + "-L.jpg"

        return Book(work_id, title, authors, cover_url)

    @log
    def _get_author_name(self, author_key: str) -> str:
        """get the author name from the author key obtained in OpenLibrary
    Args:
        author_key (str)
    Returns:
        author_name (str): The name of the author whose author_key is the key
        """

        r = requests.get(url= f"{self.BASE_URL}/authors/{author_key}.json")
        if r.status_code != 200:
            raise Exception(f"Cannot reach (HTTP {r.status_code}): {r.text}")
        else:
            raw_json = r.json()

        author_name = raw_json["personal_name"]
        return author_name

    @log
    def get_work_details(self, work_id: str) -> dict | None:
        """get some information about a work in OpenLibrary
        """
        ...

    @log
    def get_editions(self, work_id: str, limit: int = 10) -> list[dict]:
        """get different editions from a work in OpenLibrary
        """
        ...

    @log
    def search_by_author(self, author: str, limit: int = 20) -> list[Book]:
        """search works in OpenLibrary from one author
        """
        ...

    @log
    def _build_cover_url(self, cover_id: int | None, size: str = "M") -> str:
        """get the author name from the author key obtained in OpenLibrary
        """
        ...
