# Plan de code — Verticale Book (Arnaud et Cécile)

Sep 30, 2026 · @Cécile

## Périmètre et endpoints

La verticale Book couvre la recherche de livres, la fiche livre et le cache local. C'est la seule qui parle à OpenLibrary. Elle est sur le chemin critique : Reading en dépend pour ajouter un livre à une bibliothèque.

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| GET | `/books?q=` | rechercher des livres sur OpenLibrary | connecté |
| GET | `/books/{work_id}` | fiche d'un livre : infos, éditions, note moyenne | connecté |

La recherche passe par `/books?q=` plutôt que `/search` : elle reste dans le router Book, et on évite le conflit entre `/books/search` et `/books/{work_id}`.

La route `GET /book/{user_id}` du tableau, marquée « à creuser », est abandonnée : elle fait doublon avec la bibliothèque de Moussa (`GET /users/{user_id}/readings`). Les critiques d'un livre sont dans la verticale d'Axel.

## Table SQL

La table `book` est un cache : on y stocke le strict nécessaire pour ne pas rappeler OpenLibrary, limité à 3 requêtes par seconde.

```sql
CREATE TABLE book (
    book_id     SERIAL PRIMARY KEY,
    work_id     VARCHAR(255) UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    authors     TEXT NOT NULL,
    cover_url   VARCHAR(255)
);
```

`title` et `authors` sont en `TEXT` parce que certains titres ou listes d'auteurs d'OpenLibrary dépassent 255 caractères. Le business object `Book` n'a pas à changer.

La description et les éditions ne sont pas stockées : elles sont lues en direct sur OpenLibrary à l'affichage de la fiche.

## Client OpenLibrary — `client/openlibrary_client.py`

`OpenLibraryClient` est la seule classe qui appelle `requests`. Elle traduit le JSON d'OpenLibrary en objets `Book` (avec `book_id = None`) ou en dictionnaires simples.

```python
class OpenLibraryError(Exception):
    """OpenLibrary injoignable, timeout ou réponse inattendue."""

class OpenLibraryClient(metaclass=Singleton):
    BASE_URL = "https://openlibrary.org"

    def search(self, query: str, limit: int = 20) -> list[Book]
    def get_work(self, work_id: str) -> Book | None
    def get_work_details(self, work_id: str) -> dict | None
    def get_editions(self, work_id: str, limit: int = 10) -> list[dict]
    def search_by_author(self, author: str, limit: int = 20) -> list[Book]
    def _get_author_name(self, author_key: str) -> str
    def _build_cover_url(self, cover_id: int | None, size: str = "M") -> str | None
    def _get(self, path: str, params: dict | None = None) -> dict | None
```

| Méthode | Appel OpenLibrary | Ce qu'elle renvoie |
| --- | --- | --- |
| `search` | `/search.json?q=...&fields=key,title,author_name,cover_i` | `key` sans le préfixe `/works/`, auteurs joints par `", "` |
| `get_work` | `/works/{work_id}.json` | un `Book` prêt à mettre en cache ; `None` si 404 |
| `get_work_details` | `/works/{work_id}.json` | `description` et `subjects` pour la fiche |
| `get_editions` | `/works/{work_id}/editions.json` | éditeur, date, nombre de pages, ISBN (exigés par F2) |
| `search_by_author` | `/search.json?author=...` | utilisé par les recommandations |
| `_get_author_name` | `/authors/{clé}.json` | le work ne donne que des clés d'auteurs, pas les noms |
| `_build_cover_url` | aucun | `https://covers.openlibrary.org/b/id/{cover_id}-M.jpg` |
| `_get` | tous | gère timeout, erreurs HTTP, 404 → `None`, en-tête `User-Agent` |

Points d'attention dans le JSON :

- `description` est parfois une chaîne, parfois un objet `{"type": ..., "value": "..."}`. Il faut gérer les deux.
- Beaucoup de champs peuvent manquer (pas de couverture, pas d'auteur). Utiliser `.get()` partout, jamais `["clé"]` directement.
- Toute erreur réseau est convertie en `OpenLibraryError` dans `_get`, pour que le controller puisse répondre 503.

## DAO — `dao/book_dao.py`

```python
class BookDao(metaclass=Singleton):
    def create(self, book: Book) -> bool              # INSERT ... RETURNING book_id
    def find_by_id(self, book_id: int) -> Book | None
    def find_by_work_id(self, work_id: str) -> Book | None
    def _row_to_book(self, row: dict) -> Book         # privée
```

`create` remplit `book.book_id` avec l'identifiant renvoyé par la base avant de renvoyer l'objet. Le « créer seulement s'il n'existe pas » n'est pas ici : c'est un enchaînement d'étapes, donc il va dans le service.

La note moyenne se calcule sur la table `reading` : sa requête (`average_rating_by_book`) est dans `ReadingDao`, côté Moussa.

## Service — `service/book_service.py`

```python
class BookService:
    def search(self, query: str, limit: int = 20) -> list[Book]
    def get_or_create_by_work_id(self, work_id: str) -> Book | None
    def get_book_details(self, work_id: str) -> dict | None
    def find_by_id(self, book_id: int) -> Book | None
    def average_rating(self, book_id: int) -> float | None
    def search_by_author(self, author: str, limit: int = 20) -> list[Book]
```

**`get_or_create_by_work_id`** est la méthode clé, appelée aussi par Reading :

1. `BookDao().find_by_work_id(work_id)` : si le livre est en cache, on le renvoie.
2. Sinon `OpenLibraryClient().get_work(work_id)` : si OpenLibrary ne le connaît pas, on renvoie `None`.
3. Sinon `BookDao().create(book)` et on renvoie le livre, qui a maintenant un `book_id`.

**`get_book_details`** assemble la fiche : le livre (depuis le cache s'il y est, sinon depuis OpenLibrary), la description, les éditions et la note moyenne. La note moyenne vaut `None` si le livre n'est pas en base, puisque personne ne l'a alors noté.

`find_by_id` n'est pas utilisée par vos routes, mais Reading et Review en ont besoin pour reconstituer un `Book` à partir d'un `book_id`. `search_by_author` sert aux recommandations.

## Modèles Pydantic — `schema/book_model.py`

Tous les modèles sont en sortie : les deux routes sont des GET, sans corps de requête.

| Modèle | Champs | Utilisé par |
| --- | --- | --- |
| `BookSearchResultModel` | `work_id`, `title`, `authors`, `cover_url: str \| None` | `GET /books?q=` |
| `BookModel` | `book_id`, `work_id`, `title`, `authors`, `cover_url` | réutilisé par Reading et Review dans leurs réponses |
| `EditionModel` | `title`, `publisher`, `publish_date`, `number_of_pages`, `isbn` (tous optionnels) | imbriqué dans la fiche |
| `BookDetailModel` | `work_id`, `book_id: int \| None`, `title`, `authors`, `cover_url`, `description: str \| None`, `editions: list[EditionModel]`, `average_rating: float \| None` | `GET /books/{work_id}` |

`BookModel` est à livrer tôt : Moussa et Axel l'imbriqueront dans leurs propres modèles de réponse.

## Controller — `controller/book_controller.py`

```python
@router.get("", response_model=list[BookSearchResultModel], tags=["Books"])
async def search_books(q: str = Query(min_length=1),
                       current_user: User = Depends(get_current_user),
                       book_service=Depends(get_book_service))

@router.get("/{work_id}", response_model=BookDetailModel, tags=["Books"])
async def get_book(work_id: str,
                   current_user: User = Depends(get_current_user),
                   book_service=Depends(get_book_service))
```

| Fonction | Réponse | Erreurs |
| --- | --- | --- |
| `search_books` | liste, vide si aucun résultat | 422 si `q` vide ; 503 si OpenLibrary injoignable |
| `get_book` | `BookDetailModel` construit à la main à partir du dictionnaire du service | 404 si livre inconnu ; 503 si OpenLibrary injoignable |

Le router est inclus dans `main.py` avec `prefix="/books"`. `get_current_user` vient de `controller/dependencies.py`, livré par Anne-Camille.

## Tests prioritaires

Aucun test n'appelle le vrai OpenLibrary : les réponses de référence sont enregistrées en JSON dans `tests/fixtures/`.

- [ ] Client : `search` transforme correctement un JSON enregistré (`work_id` sans préfixe, auteurs joints) ; résultat sans couverture ni auteur ne plante pas
- [ ] Client : `description` sous forme de chaîne et sous forme d'objet ; 404 renvoie `None` ; timeout lève `OpenLibraryError`
- [ ] Service : `get_or_create_by_work_id` avec livre en cache, sans appel au client
- [ ] Service : `get_or_create_by_work_id` avec livre absent, appel au client puis `create`
- [ ] Service : `get_or_create_by_work_id` avec livre inconnu d'OpenLibrary, renvoie `None` sans `create`
- [ ] Service : note moyenne `None` quand aucune note
- [ ] Controller : 404 sur livre inconnu, 503 sur `OpenLibraryError`, 401 sans jeton

## Points de coordination et décisions à prendre

- **Décision à prendre à deux** : quand alimenter le cache ? Le document d'architecture le fait à l'ajout en bibliothèque (ce plan le suit : la fiche lit le cache sans l'écrire). L'autre option est d'écrire dès la consultation de la fiche : moins d'appels à OpenLibrary, mais une table qui se remplit de livres que personne n'a lus.
- **Moussa (Reading)** : son `POST /readings` reçoit un `work_id` et appelle `BookService().get_or_create_by_work_id`. Il code aussi `ReadingDao.average_rating_by_book`, dont votre fiche a besoin.
- **Moussa et Axel** : ils imbriquent `BookModel` dans leurs réponses et utilisent `BookService().find_by_id`.
- **Recommandations** : `search_by_author` est prévue pour elles. Elle peut attendre après le jalon du 16 octobre.
- **Pour travailler en parallèle** : figer d'abord les signatures du client. La personne qui code le service peut utiliser un faux client en attendant le vrai.
