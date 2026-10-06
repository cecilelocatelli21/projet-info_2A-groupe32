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
        print(title)
