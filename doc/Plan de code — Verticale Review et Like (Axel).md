# Plan de code — Verticale Review et Like (Axel)

Sep 30, 2026 · @Cécile

## Périmètre et endpoints

La verticale couvre les critiques (une par lecture au plus) et les réactions like ou dislike. Elle dépend de Reading : on ne critique qu'une lecture terminée ou abandonnée, dont on est propriétaire.

**Critiques**

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/readings/{reading_id}/review` | écrire la critique d'une lecture | propriétaire de la lecture |
| GET | `/readings/{reading_id}/review` | critique d'une lecture | connecté |
| GET | `/reviews/{review_id}` | une critique | connecté |
| PUT | `/reviews/{review_id}` | modifier le texte | auteur |
| DELETE | `/reviews/{review_id}` | supprimer | auteur |
| GET | `/users/{user_id}/reviews` | critiques d'un utilisateur | connecté |
| GET | `/books/{work_id}/reviews` | critiques d'un livre | connecté |

**Réactions**

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| PUT | `/reviews/{review_id}/like` | liker ou disliker, ou basculer de l'un à l'autre | connecté |
| DELETE | `/reviews/{review_id}/like` | retirer sa réaction | connecté |
| GET | `/reviews/{review_id}/likes` | nombre de likes et de dislikes | connecté |

Sur le tableau, like avait un POST et un PUT séparés. Un seul PUT suffit : il crée la réaction si elle n'existe pas, et la modifie sinon. Les critiques d'un livre utilisent le `work_id`, parce que c'est l'identifiant dont dispose la fiche livre.

## Tables SQL

Dans la première version de `like_table`, `user_id` et `review_id` étaient chacun `UNIQUE` : un utilisateur n'aurait pu liker qu'une seule critique dans toute sa vie. La clé primaire porte maintenant sur le couple.

```sql
CREATE TABLE review (
    review_id           SERIAL PRIMARY KEY,
    reading_id          INT UNIQUE NOT NULL REFERENCES reading(reading_id) ON DELETE CASCADE,
    text                TEXT NOT NULL,
    publication_date    DATE DEFAULT CURRENT_DATE
);

CREATE TABLE like_table (
    user_id         INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    review_id       INT NOT NULL REFERENCES review(review_id) ON DELETE CASCADE,
    like_date       DATE DEFAULT CURRENT_DATE,
    liked           BOOLEAN NOT NULL,
    PRIMARY KEY (user_id, review_id)
);
```

`reading_id UNIQUE` garantit une seule critique par lecture, directement dans la base. Supprimer une critique supprime ses likes, et supprimer une lecture supprime sa critique : rien à coder pour ces cascades.

Petite incohérence à régler : les business objects `Review` et `Like` déclarent des `datetime`, les tables des `DATE`. Soit on passe les colonnes en `TIMESTAMP` (utile pour trier des critiques publiées le même jour), soit on passe les business objects en `date`.

## DAO

**`dao/review_dao.py`**

```python
class ReviewDao(metaclass=Singleton):
    def create(self, review: Review) -> Review               # INSERT ... RETURNING review_id
    def find_by_id(self, review_id: int) -> Review | None
    def find_by_reading(self, reading_id: int) -> Review | None
    def find_by_book(self, book_id: int) -> list[Review]     # jointure sur reading
    def find_by_user(self, user_id: int) -> list[Review]     # jointure sur reading
    def count_by_user(self, user_id: int) -> int             # pour le profil
    def update(self, review: Review) -> bool                 # text
    def delete(self, review_id: int) -> bool
```

Une `Review` contient une `Reading`, qui contient un `User` et un `Book`. Les `find_*` font donc une requête qui joint `review`, `reading`, `book` et `user_table`, sur le même modèle que les requêtes de `ReadingDao`. Regarder avec Moussa pour réutiliser sa façon de construire une `Reading` à partir d'une ligne.

**`dao/like_dao.py`**

```python
class LikeDao(metaclass=Singleton):
    def create(self, like: Like) -> Like
    def find(self, user_id: int, review_id: int) -> Like | None
    def update(self, like: Like) -> bool                     # bascule liked
    def delete(self, user_id: int, review_id: int) -> bool
    def count_by_review(self, review_id: int) -> tuple[int, int]            # (likes, dislikes)
    def count_received_by_user(self, user_id: int) -> tuple[int, int]       # pour le profil
```

Pour les compteurs, une seule requête suffit : `SELECT COUNT(*) FILTER (WHERE liked), COUNT(*) FILTER (WHERE NOT liked) FROM like_table WHERE review_id = ...`.

## Services et règles métier

Deux services, un par entité, pour garder des fichiers courts.

**`service/review_service.py`**

```python
class ReviewService:
    def write_review(self, user: User, reading_id: int, text: str) -> Review
    def find_by_id(self, review_id: int) -> Review | None
    def get_by_reading(self, reading_id: int) -> Review | None
    def get_by_user(self, user_id: int) -> list[Review]
    def get_by_book(self, work_id: str) -> list[Review]
    def update_review(self, user: User, review_id: int, text: str) -> Review
    def delete_review(self, user: User, review_id: int) -> bool
```

`write_review` vérifie dans l'ordre : la lecture existe (404) ; elle appartient à l'utilisateur (403) ; son statut est « read » ou « abandoned » (400) ; elle n'a pas déjà de critique (409). `update_review` et `delete_review` : auteur uniquement, c'est-à-dire `review.reading.user.user_id == user.user_id`.

`get_by_book` retrouve le livre avec `BookDao().find_by_work_id(work_id)`. Si le livre n'est pas en cache, personne ne l'a ajouté, donc la liste est vide.

**`service/like_service.py`**

```python
class LikeService:
    def react(self, user: User, review_id: int, liked: bool) -> Like
    def remove_reaction(self, user: User, review_id: int) -> bool
    def count(self, review_id: int) -> tuple[int, int]
```

`react` : la critique doit exister (404). S'il n'y a pas encore de réaction, on la crée ; s'il y en a une, on met à jour `liked`. Envoyer deux fois la même réaction ne crée pas de doublon. `remove_reaction` sans réaction existante renvoie une 404.

Les erreurs suivent la convention proposée à l'équipe dans `utils/exceptions.py` : `NotFoundError` (404), `ForbiddenError` (403), `ConflictError` (409), `ValueError` (400).

## Modèles Pydantic

| Modèle | Fichier | Champs | Utilisé par |
| --- | --- | --- | --- |
| `ReviewCreateModel` | `schema/review_model.py` | `text: str = Field(min_length=1)` | entrée du POST et du PUT |
| `ReviewReadModel` | `schema/review_model.py` | `review_id`, `reading_id`, `user_id`, `username`, `book: BookModel`, `text`, `publication_date`, `likes: int`, `dislikes: int` | toutes les sorties critique |
| `LikeModel` | `schema/like_model.py` | `liked: bool` | entrée de `PUT /reviews/{review_id}/like` |
| `LikeReadModel` | `schema/like_model.py` | `review_id`, `user_id`, `liked`, `like_date` | sortie du PUT |
| `LikeCountModel` | `schema/like_model.py` | `likes: int`, `dislikes: int` | `GET /reviews/{review_id}/likes` |

`BookModel` vient de la verticale Book. `ReviewReadModel` affiche `username` pour qu'on voie qui a écrit la critique, mais pas l'email.

Pour remplir `likes` et `dislikes` dans une liste de critiques, appeler `count_by_review` pour chacune fonctionne très bien au volume du projet. Une requête groupée est une optimisation possible, pas une obligation.

## Controller — `controller/review_controller.py`

Un seul fichier pour les critiques et les réactions, puisque les réactions sont toujours sous `/reviews/{review_id}`. Le router est déclaré sans préfixe, car les routes commencent par `/readings`, `/reviews`, `/users` ou `/books`. Toutes prennent `current_user: User = Depends(get_current_user)`.

| Fonction | Route | Réponse | Erreurs |
| --- | --- | --- | --- |
| `write_review` | `POST /readings/{reading_id}/review` | `ReviewReadModel`, 201 | 400 statut ; 403 ; 404 ; 409 critique existante |
| `review_of_reading` | `GET /readings/{reading_id}/review` | `ReviewReadModel` | 404 |
| `review_by_id` | `GET /reviews/{review_id}` | `ReviewReadModel` | 404 |
| `update_review` | `PUT /reviews/{review_id}` | `ReviewReadModel` | 403 ; 404 |
| `delete_review` | `DELETE /reviews/{review_id}` | 204 | 403 ; 404 |
| `reviews_of_user` | `GET /users/{user_id}/reviews` | `list[ReviewReadModel]` | aucune |
| `reviews_of_book` | `GET /books/{work_id}/reviews` | `list[ReviewReadModel]` | aucune |
| `react` | `PUT /reviews/{review_id}/like` | `LikeReadModel` | 404 |
| `remove_reaction` | `DELETE /reviews/{review_id}/like` | 204 | 404 |
| `like_count` | `GET /reviews/{review_id}/likes` | `LikeCountModel` | 404 |

`GET /books/{work_id}/reviews` ne gêne pas `GET /books/{work_id}` du router Book : le chemin est plus long, donc FastAPI ne les confond pas. Une fonction `_to_model(review)` évite de répéter la construction de `ReviewReadModel`.

## Tests prioritaires

Tests des services, avec les DAO et `ReadingService` remplacés par des `MagicMock` :

- [ ] `write_review` : succès sur une lecture « read » et sur une lecture « abandoned »
- [ ] `write_review` : refusé en « to read » et en « in progress » ; refusé si critique déjà existante ; refusé sur la lecture d'un autre
- [ ] `update_review` et `delete_review` : refusés pour quelqu'un d'autre que l'auteur
- [ ] `get_by_book` : livre absent du cache, liste vide sans erreur
- [ ] `react` : création ; bascule like → dislike ; même réaction deux fois sans doublon ; critique inexistante refusée
- [ ] `remove_reaction` : réaction inexistante renvoie une erreur 404
- [ ] DAO : `count_by_review` renvoie `(0, 0)` sans réaction

## Points de coordination et questions ouvertes

- **Moussa (Reading)** : `ReadingService().find_by_id` pour vérifier propriétaire et statut, et sa façon de construire une `Reading` à partir d'une ligne SQL.
- **Arnaud et Cécile (Book)** : `BookModel` pour les réponses, `BookDao().find_by_work_id` pour les critiques d'un livre.
- **Paul (profil)** : `ReviewDao.count_by_user` et `LikeDao.count_received_by_user` pour les compteurs du profil.
- **Anne-Camille (User)** : `get_current_user` dans `controller/dependencies.py`.
- **Question ouverte** : peut-on liker sa propre critique ? Si non, `react` doit le refuser (400).
- **Question ouverte** : `DATE` ou `TIMESTAMP` pour `publication_date` et `like_date` (voir la section Tables SQL).
- **Calendrier** : les critiques font partie du jalon du 23 octobre ; les likes peuvent attendre le sprint du 3 au 5 novembre.
