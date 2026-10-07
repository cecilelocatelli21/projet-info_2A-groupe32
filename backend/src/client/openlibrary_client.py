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

        title = raw_json["title"]
        author_key = raw_json["author"["key"]]
        author = self._get_author_name(author_key=author_key)
        print(title)
        print(author_key)
        print(author)

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
    def _get_author_name(self, author_key: str) -> str:
        """get the author name from the author key obtained in OpenLibrary
        """
        ...

    @log
    def _build_cover_url(self, cover_id: int | None, size: str = "M") -> str:
        """get the author name from the author key obtained in OpenLibrary
        """
        ...
