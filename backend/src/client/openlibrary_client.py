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

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            Book | None: the book without its book_id ,
                or None if OpenLibrary does not know this work_id
        """
        r = requests.get(url= f"{self.BASE_URL}/works/{work_id}.json")
        if r.status_code == 404:
            return None
        elif r.status_code != 200:
            raise Exception(f"Cannot reach (HTTP {r.status_code}): {r.text}")
        else:
            raw_json = r.json()
            # print(json.dumps(raw_json, indent=2))  # Pretty print

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
    def get_editions(self, work_id: str, limit: int = 10) -> dict | None:
        """get different editions from a work in OpenLibrary

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
            limit (int): maximum number of editions to return.
        Returns:
            dict: {
                "total": total number of editions known by OpenLibrary,
                "editions": list of at most `limit` dicts, with keys "title",
                    "publisher", "publish_date", "number_of_pages" and "isbn"
                    (each may be None),
            }
            None if OpenLibrary does not know this work_id.
        """
        r = requests.get(
            url=f"{self.BASE_URL}/works/{work_id}/editions.json",
            params={"limit": limit},
        )
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise Exception(f"Cannot reach (HTTP {r.status_code}): {r.text}")

        raw_json = r.json()
        editions = []
        for entry in raw_json.get("entries", []):
            # publishers, isbn10, isbn13 are lists: we keep the first value
            publishers = entry.get("publishers",[])
            publisher = publishers[0] if publishers else None

            isbns = entry.get("isbn_13") or entry.get("isbn_10") or []
            isbn = isbns[0] if isbns else None

            editions.append({
                "title": entry.get("title"),
                "publisher": publisher,
                "publish_date": entry.get("publish_date"),
                "number_of_pages": entry.get("number_of_pages"),
                "isbn": isbn
            })

        return {"total": raw_json.get("size", len(editions)), "editions": editions}


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
