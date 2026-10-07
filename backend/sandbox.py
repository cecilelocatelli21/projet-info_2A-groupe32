# uv run --project backend python backend/sandbox.py

from business_object.book import Book
from business_object.user import User
from client.openlibrary_client import OpenLibraryClient
from dao.book_dao import BookDao
from service.book_service import BookService
from utils.env_variables import load_environment_variables

load_environment_variables()   # Required to load the variables needed (env) to connect to the database 

openlibraryclient = OpenLibraryClient()

book = openlibraryclient.get_work("OL258850W")
print(book.__str__())
print(book.work_id + " " + book.title + " " + book.authors + " " +  book.cover_url)
print(book.as_list())

service = BookService()
print(service.get_or_create_by_work_id("OL10263W").as_list())
print(service.get_or_create_by_work_id("OL10263W").book_id)
print(service.get_or_create_by_work_id("OL258850W").as_list())
print(service.get_or_create_by_work_id("OL258850W").book_id)

edition = openlibraryclient.get_editions("OL10263W")
print(edition["total"])
print(edition["editions"])

print(service.get_book_details("OL258850W"))