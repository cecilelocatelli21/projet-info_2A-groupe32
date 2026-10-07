# uv run --project backend python backend/sandbox.py

from business_object.user import User
from business_object.book import Book
from dao.book_dao import BookDao
from utils.env_variables import load_environment_variables
from client.openlibrary_client import OpenLibraryClient

load_environment_variables()   # Required to load the variables needed (env) to connect to the database 

openlibraryclient = OpenLibraryClient()

book = openlibraryclient.get_work("OL258850W")
book.__str__()
print(book.work_id + " " + book.title + " " + book.authors + " " +  book.cover_url)
