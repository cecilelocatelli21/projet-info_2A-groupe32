from business_object.utilisateur import Utilisateur
from dao.librairie_dao import UtilisateurDao
from utils.env_variables import load_environment_variables

load_environment_variables()   # Required to load the variables needed (env) to connect to the database 

utilisateurdao = UtilisateurDao()
utilisateurs = utilisateurdao.find_all()

for u in utilisateurs:
    print(u.pseudo)