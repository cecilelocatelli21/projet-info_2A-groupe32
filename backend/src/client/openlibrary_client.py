import requests

from business_object.book import Book
from utils.log_utils import log
from utils.singleton import Singleton


class OpenLibraryError(Exception):
    """OpenLibrary unjoignable, timeout or unexpected response"""


class OpenLibraryClient(metaclass=Singleton):
    BASE_URL = "https://openlibrary.org"

    @log
    def search(self, query: str, limit: int = 20) -> list[Book]:
        """search books in open library

        Args:
            query (str): the sentence the user typed to make a search in OpenLibrary (for instance: "le petit prince")
            limit (int): the maximum values we get in the response from OpenLibrary
        Returns:
            A list of books corresponding to the response given by OpenLibrary
        """
        ## request effectue déjà ce découpage + gère les accent et caractères spéciaux en passant query en paramètres
        # # We cut the sentence written by the user into words that we insert into a html query for OpenLibrary
        # words_list = query.split(" ")
        # words_query = ""
        # for w in words_list:
        #     words_query = f"{words_query}{w}+"
        # words_query = words_query[:-1]
        # # words_query is a string corresponding at what we have to put in the html query for the search

        raw_json = self._get(
            path="/search.json",
            params={
                "q": query,
                "limit": limit}
        )
        if raw_json is None:
            return []

        # _raw_json_to_list_of_book transform a raw_json into a list of books
        books_list = self._raw_json_to_list_of_book(raw_json=raw_json, limit=limit)

        return books_list

    @log
    def get_work(self, work_id: str) -> Book | None:
        """get a work in OpenLibrary if it exists

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            Book | None: the book without its book_id ,
                or None if OpenLibrary does not know this work_id
        """
        raw_json = self._get(path=f"/works/{work_id}.json")
        if raw_json is None:
            return None

        title = raw_json.get("title")

        authors_in_work = raw_json.get("authors") or []
        authors = None
        if authors_in_work:
            author_key = authors_in_work[0]["author"]["key"].split("/")[2]
            authors = self._get_author_name(author_key=author_key)

        # OpenLibrary returns a list of covers in the raw_json, we choose the last one of the list.
        list_cover_id = raw_json.get("covers") or []
        cover_url = self._build_cover_url(cover_id=list_cover_id[-1] if list_cover_id else None)

        return Book(work_id, title, authors, cover_url)

    @log
    def get_work_details(self, work_id: str) -> dict | None:
        """get some information about a work in OpenLibrary

        Args:
            work_id (str): OpenLibrary identifier of the work (e.g. "OL45804W").
        Returns:
            dict: {
                "subjects" (list[str] = []): the subjects covered by the book
                "description" (str | None) : if it does exist, a description of the book
            }
            None if OpenLibrary does not know this work_id.
        """
 
        raw_json = self._get(f"/works/{work_id}.json")
        if raw_json is None:
            return None

        # description can be a string or a dict where the description is in the key "value"
        description = raw_json.get("description")
        if isinstance(description, dict):
            description = description.get("value")
        work_details = {
            "subjects" : raw_json.get("subjects",[]),
            "description" : description
        }
        return work_details

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
        raw_json = self._get(
            path=f"/works/{work_id}/editions.json",
            params={"limit": limit}
        )
        if raw_json is None:
            return None

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

        Args:
            author (str): The name of the author we are looking for.
            limit (int): maximum number of books to return.
        Returns:
            A list of books written by this author or about this author
            An empty list if nothing has been found
        """
        raw_json = self._get(
            path="/search.json",
            params={
                "q": author,
                "limit": limit})

        if raw_json is None:
            return []

        # _raw_json_to_list_of_book transform a raw_json into a list of books
        books_list = self._raw_json_to_list_of_book(raw_json=raw_json, limit=limit)

        return books_list

    @log
    def _get_author_name(self, author_key: str) -> str | None:
        """get the author name from the author key obtained in OpenLibrary
    Args:
        author_key (str)
    Returns:
        author_name (str): The name of the author whose author_key is the key
        """
        raw_json = self._get(
            path=f"/authors/{author_key}.json"
        )
        if raw_json is None:
            return None
        # author_name can be found under "personal_name" or "name"
        return raw_json.get("personal_name") or raw_json.get("name")

    @log
    def _build_cover_url(self, cover_id: int | None, size: str = "M") -> str | None:
        """get the url of a cover

        Args:
            cover_id (int): OpenLibrary identifier of the cover (e.g. "7165018").
            size (str): the size of the image ("S" -> small, "M" -> medium, "L" -> large). Default size is "M".
        Returns:
            the precise url for the image of the cover.
        """

        if cover_id is None:
            return None
        else:
            return f"https://covers.openlibrary.org/b/ID/{cover_id}-{size}.jpg"

    @log
    def _raw_json_to_list_of_book(self, raw_json: dict, limit: int = 20) -> list[Book]:
        """transform a json returned by OpenLibrary into a list of books

        Args:
            raw_json (dict): OpenLibrary response to the query made by the user
            limit (int): maximum number of responses returned by OpenLibrary.
        Returns:
            a list of suggested books in a format corresponding to Business Objects Book
        """

        book_list = []
        docs = raw_json.get("docs") or []
        results_number = min(len(docs), limit)
        for i in range(results_number):
            # We split the key that is like "/works/{work_id}" to get only the work_id
            work_id = docs[i].get("key").split("/")[2]
            title = docs[i].get("title")
            authors = docs[i].get("author_name") or []
            # We transform the list of authors into a string that contains all the authors
            authors_string = ""
            for a in authors:
                authors_string = f"{authors_string}{a} et "
            authors_string = authors_string[:-4]
            cover_i = docs[i].get("cover_i")
            cover_url = self._build_cover_url(cover_i)
            book = Book(work_id=work_id, title=title, authors=authors_string, cover_url=cover_url)

            book_list.append(book)

        return book_list


    @log
    def _get(self, path: str, params: dict | None = None) -> dict | None:
        """Send a GET request to OpenLibrary and return the JSON response.

        Args:
            path (str): path after BASE_URL (e.g. "/works/OL45804W.json").
            params (dict | None): query parameters (e.g. {"limit": 20}).

        Returns:
            dict | None: the JSON response, or None if OpenLibrary answers 404.

        Raises:
            OpenLibraryError: if OpenLibrary is unreachable or returns an unexpected status code.
        """
        try:
            r = requests.get(
                url=f"{self.BASE_URL}{path}",
                params=params,
                headers={"User-Agent": "Ex-Libris (projet ENSAI)"},
                timeout=10,
            )
        except requests.RequestException as e:
            # OpenLibrary does not answer at all (no network, timeout...)
            raise OpenLibraryError(f"Cannot reach OpenLibrary: {e}") from e

        if r.status_code == 404:
            return None
        if r.status_code != 200:
            raise OpenLibraryError(f"OpenLibrary error (HTTP {r.status_code}): {r.text}")
        return r.json()
