# uv run --project backend python backend/sandbox.py

from business_object.user import User
from dao.librairie_dao import UserDao
from utils.env_variables import load_environment_variables

load_environment_variables()   # Required to load the variables needed (env) to connect to the database 

userdao = UserDao()
users = userdao.find_all()

for u in users:
    print(u.username)
