import requests

url = "https://openlibrary.org/search.json"
params = {"q": "le petit prince", "sort": "editions"}

reponse = requests.get(url, params=params)
data = reponse.json()  # transforme le JSON en dictionnaire Python

print(data["numFound"])  # nombre total de résultats
print(data["docs"][0]["title"])  # titre du premier résultat
print(data["docs"][0].keys())  # tous les champs disponibles pour ce livre
