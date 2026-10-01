# Plan de code — Verticale Follow (Paul)

Sep 30, 2026 · @Cécile

## Périmètre et endpoints

La verticale Follow gère les abonnements entre utilisateurs. C'est la plus légère des cinq, ce qui laisse de la place pour les tâches à confirmer en fin de document (compteurs du profil, données de test).

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/users/{user_id}/follow` | s'abonner à `user_id` | connecté |
| DELETE | `/users/{user_id}/follow` | se désabonner de `user_id` | connecté |
| GET | `/users/{user_id}/following` | personnes que `user_id` suit | connecté |
| GET | `/users/{user_id}/followers` | personnes qui suivent `user_id` | connecté |

Sur le tableau, le POST et le DELETE prenaient `{follower_id}&{followed_id}`. Avec le jeton, l'abonné est toujours l'utilisateur connecté : seul l'identifiant de la personne suivie reste dans l'URL. Sinon, n'importe qui pourrait abonner quelqu'un d'autre.

## Table SQL et business object

La première version de la table n'avait pas de clé primaire : on pouvait s'abonner deux fois à la même personne. Les deux règles du métier sont maintenant garanties par la base elle-même.

```sql
CREATE TABLE follow (
    follower_id     INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    followed_id     INT NOT NULL REFERENCES user_table(user_id) ON DELETE CASCADE,
    follow_date     DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (follower_id, followed_id),   -- pas de doublon
    CHECK (follower_id <> followed_id)        -- pas d'abonnement à soi-même
);
```

Le service vérifie quand même ces règles avant d'insérer, pour renvoyer un message clair au lieu d'une erreur SQL.

**Incohérence à corriger** : le business object `Follow` a un `follow_id`, mais la table n'en a pas, puisque le couple (abonné, suivi) sert de clé. Le plus simple est de retirer `follow_id` du business object. Autre détail : `follow_date` est un `datetime` dans le business object et un `DATE` dans la table ; à aligner.

## DAO — `dao/follow_dao.py`

```python
class FollowDao(metaclass=Singleton):
    def create(self, follow: Follow) -> Follow
    def delete(self, follower_id: int, followed_id: int) -> bool
    def exists(self, follower_id: int, followed_id: int) -> bool
    def find_following(self, user_id: int) -> list[User]    # jointure sur user_table
    def find_followers(self, user_id: int) -> list[User]    # jointure sur user_table
    def find_followed_ids(self, user_id: int) -> list[int]  # pour les recommandations
    def count_following(self, user_id: int) -> int          # pour le profil
    def count_followers(self, user_id: int) -> int          # pour le profil
```

`find_following` et `find_followers` renvoient directement des `User`, grâce à une jointure :

```sql
SELECT u.*
  FROM follow f
  JOIN user_table u ON u.user_id = f.followed_id
 WHERE f.follower_id = %(user_id)s
 ORDER BY u.username;
```

Pour `find_followers`, on inverse les deux colonnes. `find_followed_ids` peut attendre les recommandations.

## Service et règles métier — `service/follow_service.py`

```python
class FollowService:
    def follow(self, user: User, followed_id: int) -> Follow
    def unfollow(self, user: User, followed_id: int) -> bool
    def get_following(self, user_id: int) -> list[User]
    def get_followers(self, user_id: int) -> list[User]
```

Règles à coder dans `follow`, dans cet ordre :

1. La personne à suivre existe : `UserService().find_by_id(followed_id)`, sinon `NotFoundError` (404).
2. On ne s'abonne pas à soi-même : `followed_id == user.user_id` → `ValueError` (400).
3. Pas de doublon : `FollowDao().exists(...)` → `ConflictError` (409).
4. Sinon, créer le `Follow` avec la date du jour et appeler `FollowDao().create`.

`unfollow` lève `NotFoundError` si l'abonnement n'existe pas. `get_following` et `get_followers` renvoient une liste vide pour quelqu'un sans abonnement ; si `user_id` n'existe pas, renvoyer une 404 est plus clair qu'une liste vide.

Les erreurs suivent la convention proposée à l'équipe dans `utils/exceptions.py` : `NotFoundError` (404), `ForbiddenError` (403), `ConflictError` (409), `ValueError` (400).

## Modèles Pydantic — `schema/follow_model.py`

Aucun modèle d'entrée : l'identifiant de la personne suivie est dans l'URL, l'abonné vient du jeton.

| Modèle | Champs | Utilisé par |
| --- | --- | --- |
| `FollowReadModel` | `follower_id`, `followed_id`, `follow_date` | sortie de `POST /users/{user_id}/follow` |
| `UserPublicModel` (verticale User) | `user_id`, `username`, `bio` | listes `following` et `followers` |

Les listes réutilisent `UserPublicModel` d'Anne-Camille : ainsi, l'email des abonnés n'est jamais exposé.

## Controller — `controller/follow_controller.py`

Le router est déclaré sans préfixe, avec le chemin complet de chaque route. Toutes prennent `current_user: User = Depends(get_current_user)`, fourni par Anne-Camille dans `controller/dependencies.py`.

| Fonction | Route | Réponse | Erreurs |
| --- | --- | --- | --- |
| `follow_user` | `POST /users/{user_id}/follow` | `FollowReadModel`, 201 | 400 soi-même ; 404 utilisateur inconnu ; 409 déjà abonné |
| `unfollow_user` | `DELETE /users/{user_id}/follow` | 204 | 404 abonnement inexistant |
| `following` | `GET /users/{user_id}/following` | `list[UserPublicModel]` | 404 utilisateur inconnu |
| `followers` | `GET /users/{user_id}/followers` | `list[UserPublicModel]` | 404 utilisateur inconnu |

Ces routes commencent par `/users/{user_id}/...` sans gêner celles d'Anne-Camille : leur chemin est plus long, donc FastAPI ne les confond pas avec `GET /users/{user_id}`.

## Tests prioritaires

Tests du service, avec `FollowDao` et `UserService` remplacés par des `MagicMock` :

- [ ] `follow` : succès
- [ ] `follow` : abonnement à soi-même refusé
- [ ] `follow` : doublon refusé
- [ ] `follow` : utilisateur cible inexistant refusé
- [ ] `unfollow` : abonnement inexistant refusé
- [ ] `get_following` et `get_followers` : liste vide pour quelqu'un sans abonnement
- [ ] DAO : `find_following` et `find_followers` ne mélangent pas les deux sens de la relation

## Points de coordination et tâches à confirmer

- **Anne-Camille (User)** : `get_current_user`, `UserService().find_by_id` et `UserPublicModel`.
- **Recommandations** : `find_followed_ids` servira à proposer les livres bien notés par les comptes suivis.

**Tâches supplémentaires à confirmer en équipe**. Le document d'architecture les rattachait à cette tranche, la plus légère :

1. **Compteurs du profil** : une route `GET /users/{user_id}/stats` renvoyant un `ProfileStatsModel` (`followers`, `following`, `books`, `reviews`, `likes_received`, `dislikes_received`). Le service, par exemple `service/profile_service.py`, appelle `FollowDao.count_followers` et `count_following`, `ReadingDao.count_by_user` (Moussa), `ReviewDao.count_by_user` et `LikeDao.count_received_by_user` (Axel).
2. **Données de test** : compléter `reset_database` et un jeu de données (quelques utilisateurs, livres, lectures, critiques, likes, abonnements). Tout le monde en a besoin pour tester, donc c'est utile tôt, avant le jalon du 16 octobre.

- **Question ouverte** : le fil d'activité (FO1 du sujet) est absent de la liste V2. S'il est gardé, il irait ici : `get_feed(user)` et `GET /feed`, avec les dernières critiques et lectures des comptes suivis.
