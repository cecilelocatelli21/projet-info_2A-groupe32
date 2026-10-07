# Plan de code — Verticale Reading (Moussa)

Sep 30, 2026 · @Cécile

## Périmètre et endpoints

La verticale Reading gère la bibliothèque : ajouter un livre, changer son statut, le noter, le retirer. Elle dépend de User (utilisateur connecté) et de Book (livre à ajouter), et Review dépend d'elle.

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/readings` | ajouter un livre à sa bibliothèque | connecté |
| GET | `/readings/{reading_id}` | consulter une lecture | connecté |
| GET | `/users/{user_id}/readings?status=` | bibliothèque de quelqu'un, filtrable par statut | connecté |
| PATCH | `/readings/{reading_id}` | changer statut, note ou date de lecture | propriétaire |
| DELETE | `/readings/{reading_id}` | retirer un livre de sa bibliothèque | propriétaire |

Différences avec le tableau :

- Le POST ne prend plus `{book_id}&{user_id}` dans l'URL. L'utilisateur vient du jeton, et le livre est désigné par son `work_id` dans le corps de la requête, car après une recherche on n'a pas encore de `book_id`.
- La modification passe en PATCH, parce qu'on n'envoie que les champs qui changent. Un PUT reste possible si l'équipe préfère.

## Table SQL

Dans la première version du script, `user_id` et `book_id` étaient chacun `UNIQUE` séparément : un utilisateur n'aurait pu avoir qu'une seule lecture. La contrainte porte maintenant sur le couple.

```sql
CREATE TABLE reading (
    reading_id      SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    book_id         INT NOT NULL REFERENCES book(book_id),
    status          VARCHAR(50) NOT NULL,
    date_added      DATE DEFAULT CURRENT_DATE,
    date_read       DATE,
    rating          INT CHECK (rating BETWEEN 0 AND 5),
    UNIQUE (user_id, book_id)
);
```

Supprimer une lecture supprime sa critique, qui supprime ses likes : c'est géré par les `ON DELETE CASCADE` des tables `review` et `like_table`, sans code à écrire.

Les quatre statuts sont ceux du business object : `"to read"`, `"in progress"`, `"read"`, `"abandoned"`.

## DAO — `dao/reading_dao.py`

```python
class ReadingDao(metaclass=Singleton):
    def create(self, reading: Reading) -> bool          # INSERT ... RETURNING reading_id
    def find_by_id(self, reading_id: int) -> Reading | None
    def find_by_user(self, user_id: int, status: str | None = None) -> list[Reading]
    def find_by_user_and_book(self, user_id: int, book_id: int) -> Reading | None
    def update(self, reading: Reading) -> bool             # status, date_read, rating
    def delete(self, reading_id: int) -> bool
    def average_rating_by_book(self, book_id: int) -> float | None   # pour Book
    def count_by_user(self, user_id: int) -> int                     # pour le profil
    def find_by_users(self, user_ids: list[int],
                      min_rating: int | None = None) -> list[Reading] # pour les recommandations
    def _row_to_reading(self, row: dict) -> Reading        # privée
```

Un `Reading` contient des objets `User` et `Book`, pas seulement leurs identifiants. Pour les construire sans multiplier les requêtes, les méthodes `find_*` font une seule requête avec jointure :

```sql
SELECT r.*, b.work_id, b.title, b.authors, b.cover_url,
       u.username, u.email, u.bio
  FROM reading r
  JOIN book b       ON b.book_id = r.book_id
  JOIN user_table u ON u.user_id = r.user_id
 WHERE r.user_id = %(user_id)s;
```

`average_rating_by_book` : `SELECT AVG(rating) FROM reading WHERE book_id = ... AND rating IS NOT NULL`. `AVG` renvoie `NULL` s'il n'y a aucune note, ce qui donne `None` en Python. `find_by_users` peut attendre les recommandations.

## Service et règles métier — `service/reading_service.py`

```python
class ReadingService:
    def add_book(self, user: User, work_id: str, status: str = "to read") -> Reading
    def find_by_id(self, reading_id: int) -> Reading | None
    def get_library(self, user_id: int, status: str | None = None) -> list[Reading]
    def update_reading(self, user: User, reading_id: int, status: str | None = None,
                       rating: int | None = None, date_read: date | None = None) -> Reading
    def delete_reading(self, user: User, reading_id: int) -> bool
```

Règles à coder :

1. **Ajout** : obtenir le livre avec `BookService().get_or_create_by_work_id(work_id)` ; livre introuvable refusé ; livre déjà dans la bibliothèque refusé (`find_by_user_and_book`) ; `date_added` = aujourd'hui.
2. **Passage à « read »** : remplir `date_read` avec la date du jour si elle n'est pas fournie.
3. **Note** : acceptée seulement si le statut (après modification) est « read » ou « abandoned ». La borne 0 à 5 est déjà vérifiée par Pydantic et par la base.
4. **Propriétaire** : modifier ou supprimer la lecture de quelqu'un d'autre est refusé.

**Convention d'erreurs proposée pour toute l'équipe**, dans `utils/exceptions.py` : `NotFoundError` (404), `ForbiddenError` (403), `ConflictError` (409), et `ValueError` pour une règle métier non respectée (400). Le service lève, le controller traduit en code HTTP. Exemple : doublon → `ConflictError`, note sur un livre « to read » → `ValueError`.

## Modèles Pydantic — `schema/reading_model.py`

Les statuts sont déclarés une fois : `ReadingStatus = Literal["to read", "in progress", "read", "abandoned"]`. Pydantic refuse alors tout autre texte, avec une erreur 422 automatique.

| Modèle | Champs | Utilisé par |
| --- | --- | --- |
| `ReadingCreateModel` | `work_id: str`, `status: ReadingStatus = "to read"` | entrée de `POST /readings` |
| `ReadingUpdateModel` | `status: ReadingStatus \| None = None`, `rating: int \| None = Field(None, ge=0, le=5)`, `date_read: date \| None = None` | entrée de `PATCH /readings/{reading_id}` |
| `ReadingReadModel` | `reading_id`, `user_id`, `book: BookModel`, `status`, `date_added`, `date_read`, `rating` | toutes les sorties |

`BookModel` vient de `schema/book_model.py` (verticale Book). Dans `ReadingReadModel`, on ne renvoie que `user_id`, pas l'objet `User` entier, pour ne pas exposer l'email.

## Controller — `controller/reading_controller.py`

Toutes les routes prennent `current_user: User = Depends(get_current_user)`, fourni par Anne-Camille dans `controller/dependencies.py`.

| Fonction | Route | Réponse | Erreurs |
| --- | --- | --- | --- |
| `add_reading` | `POST /readings` | `ReadingReadModel`, code 201 | 404 livre introuvable ; 409 déjà dans la bibliothèque ; 503 OpenLibrary injoignable |
| `get_reading` | `GET /readings/{reading_id}` | `ReadingReadModel` | 404 |
| `get_library` | `GET /users/{user_id}/readings?status=` | `list[ReadingReadModel]` | aucune (liste vide) |
| `update_reading` | `PATCH /readings/{reading_id}` | `ReadingReadModel` | 400 règle ; 403 pas propriétaire ; 404 |
| `delete_reading` | `DELETE /readings/{reading_id}` | 204 | 403 ; 404 |

Deux points pratiques :

- La route `/users/{user_id}/readings` ne commence pas par `/readings`. Le plus simple est de déclarer le router sans préfixe et d'écrire le chemin complet de chaque route.
- La réponse se construit à la main : `user_id=reading.user.user_id` et `book=BookModel(...)` à partir de `reading.book`. Une petite fonction `_to_model(reading)` évite de le répéter dans chaque route.

## Tests prioritaires

Tests du service, avec `ReadingDao` et `BookService` remplacés par des `MagicMock` :

- [ ] `add_book` : succès ; livre déjà dans la bibliothèque refusé ; livre introuvable refusé
- [ ] `add_book` directement en statut « read » : `date_read` remplie
- [ ] `update_reading` : `date_read` remplie au passage à « read »
- [ ] `update_reading` : note refusée en « to read » et en « in progress », acceptée en « read » et en « abandoned »
- [ ] `update_reading` et `delete_reading` : lecture d'un autre utilisateur refusée
- [ ] DAO : `average_rating_by_book` renvoie `None` sans note, et la bonne moyenne avec plusieurs notes

## Points de coordination et questions ouvertes

- **Arnaud et Cécile (Book)** : ils fournissent `BookService().get_or_create_by_work_id`, `find_by_id` et `BookModel`. Ils ont besoin en retour de `ReadingDao.average_rating_by_book` pour la fiche livre.
- **Axel (Review)** : une critique n'est possible que sur une lecture « read » ou « abandoned » dont on est propriétaire. Il utilisera `ReadingService().find_by_id` pour le vérifier.
- **Paul (profil)** : `count_by_user` pour le nombre de livres affiché sur le profil.
- **Jalon du 16 octobre** : l'ajout d'un livre à la bibliothèque en fait partie. `add_book` et `get_library` sont prioritaires.
- **Question ouverte** : si une lecture repasse de « read » à « in progress », faut-il effacer `date_read` et la note ? À trancher en équipe.
- **Question ouverte** : F3 demande de « renseigner ses dates de lecture », mais la table n'a que `date_added` et `date_read`. Ajouter une colonne `date_started` ?
