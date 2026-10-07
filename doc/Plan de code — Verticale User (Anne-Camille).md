# Plan de code — Verticale User (Anne-Camille)

Sep 30, 2026 · @Cécile · mis à jour le 7 octobre 2026 (vérification du mot de passe alignée sur le template)

## Périmètre et endpoints

La verticale User couvre le compte, l'authentification par jeton et la fiche utilisateur. Elle est sur le chemin critique : toutes les autres verticales ont besoin de `get_current_user` pour leurs routes « connecté ».

Les URL suivent la convention au pluriel (`/users`). Avec un jeton, l'utilisateur connecté est identifié par le jeton, pas par un `user_id` dans l'URL : les actions sur son propre compte passent donc par `/users/me`.

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/users` | créer un compte | public |
| POST | `/login` | se connecter, renvoie le jeton | public |
| POST | `/logout` | se déconnecter (efface le jeton) | connecté |
| GET | `/users/me` | son propre profil, avec email | connecté |
| PUT | `/users/me` | modifier bio ou email | connecté |
| PUT | `/users/me/password` | changer de mot de passe | connecté |
| DELETE | `/users/me` | supprimer son compte | connecté |
| GET | `/users/{user_id}` | fiche publique d'un utilisateur | connecté |
| GET | `/users?username=` | rechercher des utilisateurs (FO1) | connecté |

Sur le tableau, modifier et supprimer passaient par `/user/{user_id}`. Si l'équipe garde cette forme, le service doit vérifier que `user_id` est bien celui de l'utilisateur connecté.

## Table SQL et business object

La table `user_table` gagne une colonne `access_token`, vide quand l'utilisateur est déconnecté. L'email devient unique.

```sql
CREATE TABLE user_table (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(30) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    bio             TEXT,
    access_token    VARCHAR(255) UNIQUE
);
```

Le business object `User` doit suivre : ajouter `access_token=None` au constructeur. Il n'apparaîtra jamais dans les réponses de l'API, sauf à la connexion.

Le mot de passe est haché avec `hash_password(password, username)`, le pseudo servant de sel. Conséquence : le pseudo ne doit pas être modifiable, sinon plus personne ne pourrait se reconnecter.

## DAO — `dao/user_dao.py`

`UserDao` ne fait que du SQL, sans règle métier. `find_all` et `find_by_id` existent déjà.

```python
class UserDao(metaclass=Singleton):
    def create(self, user: User) -> User                  # INSERT ... RETURNING user_id
    def find_all(self) -> list[User]                      # déjà codé
    def find_by_id(self, user_id: int) -> User | None     # déjà codé
    def find_by_username(self, username: str) -> User | None
    def find_by_email(self, email: str) -> User | None
    def find_by_token(self, token: str) -> User | None
    def login(self, username: str, password_hash: str) -> User | None   # comme le template
    def search_by_username(self, pattern: str) -> list[User]   # ILIKE '%motif%'
    def update(self, user: User) -> bool                  # bio, email, password_hash, access_token
    def delete(self, user_id: int) -> bool
    def _row_to_user(self, row: dict) -> User             # privée
```

**`login` suit le template du professeur.** Le DAO ne fait qu'une requête : « donne-moi l'utilisateur qui a *ce* pseudo **et** *ce* mot de passe brouillé ». S'il n'y en a pas (pseudo inconnu ou mauvais mot de passe), il renvoie `None`.

```sql
SELECT * FROM user_table
 WHERE username = %(username)s AND password_hash = %(password_hash)s;
```

Le DAO reçoit le mot de passe **déjà brouillé** : c'est le service qui appelle `hash_password`. Le DAO ne voit jamais le mot de passe en clair.

`find_by_username` reste utile pour vérifier qu'un pseudo n'est pas déjà pris à la création de compte.

`_row_to_user` évite de réécrire la construction de `User` dans chaque méthode, comme c'est le cas aujourd'hui dans `find_all` et `find_by_id`.

`delete` n'a rien d'autre à faire : les lectures, critiques, likes et abonnements de l'utilisateur partent avec lui grâce aux `ON DELETE CASCADE` du script SQL.

## Service — `service/user_service.py`

`UserService` porte toutes les règles. Les méthodes qui touchent au compte courant reçoivent l'objet `User` fourni par `get_current_user`.

```python
class UserService:
    def create_account(self, username: str, email: str, password: str) -> User
    def login(self, username: str, password: str) -> User | None
    def logout(self, user: User) -> bool
    def find_by_id(self, user_id: int) -> User | None      # déjà codé
    def find_by_token(self, token: str) -> User | None
    def update_profile(self, user: User, bio: str | None = None,
                       email: str | None = None) -> User
    def change_password(self, user: User, old_password: str,
                        new_password: str) -> bool
    def delete_account(self, user: User) -> bool
    def search(self, pattern: str) -> list[User]
```

Règles à coder :

- `create_account` : refuse un pseudo ou un email déjà pris (lève une `ValueError` avec un message clair), hache le mot de passe, puis appelle `UserDao().create`.
- `login` : brouille le mot de passe avec `hash_password(password, username)`, appelle `UserDao().login`, et si un utilisateur est trouvé, génère `secrets.token_urlsafe(32)`, l'enregistre avec `update` et renvoie l'utilisateur (code ci-dessous).
- `logout` : remet `access_token` à `None`.
- `update_profile` : si l'email change, vérifier qu'il n'est pas déjà utilisé par quelqu'un d'autre.
- `change_password` : vérifie l'ancien mot de passe en réutilisant `UserDao().login(user.username, hash_password(old_password, user.username))`. S'il renvoie `None`, l'ancien mot de passe est faux et on refuse. Sinon, on brouille le nouveau et on l'enregistre avec `update`.

Le `login` du service, repris du code commenté du template :

```python
@log
def login(self, username: str, password: str) -> User | None:
    user = UserDao().login(username, hash_password(password, username))
    if user is None:
        return None                                  # pseudo inconnu ou mauvais mot de passe
    user.access_token = secrets.token_urlsafe(32)   # on remet un jeton
    UserDao().update(user)
    return user
```

Le contrôle de longueur du mot de passe reste dans le modèle Pydantic, où il est déjà.

## Modèles Pydantic — `schema/user_model.py`

Trois modèles existent déjà. Il faut surtout séparer ce qu'on montre à tout le monde de ce qu'on montre à l'utilisateur lui-même : aujourd'hui, `GET /users/{user_id}` exposerait l'email de n'importe qui.

| Modèle | Champs | Utilisé par |
| --- | --- | --- |
| `UserModel` (existe, à compléter) | `username`, `email: EmailStr`, `password` + validateur de longueur | entrée de `POST /users` |
| `UserLoginModel` (existe) | `username`, `password` | entrée de `POST /login` |
| `TokenModel` | `access_token: str`, `token_type: str = "bearer"` | sortie de `POST /login` |
| `UserReadModel` (existe) | `user_id`, `username`, `bio`, `email` | sortie de `/users/me` uniquement |
| `UserPublicModel` | `user_id`, `username`, `bio` | sortie de `GET /users/{user_id}` et de la recherche |
| `UserUpdateModel` | `bio: str \| None = None`, `email: EmailStr \| None = None` | entrée de `PUT /users/me` |
| `PasswordChangeModel` | `old_password`, `new_password` + même validateur | entrée de `PUT /users/me/password` |

Dans `UserModel`, retirer `user_id` : c'est la base qui l'attribue, le client n'a pas à l'envoyer.

## Controller et dépendance d'authentification

**`controller/dependencies.py`**, à livrer en premier puisque toute l'équipe l'importe :

```python
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    user = UserService().find_by_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
```

`HTTPBearer` lit l'en-tête `Authorization: Bearer <jeton>` et ajoute le bouton « Authorize » dans Swagger (`/docs`), ce qui permet à tout le monde de tester les routes protégées. Les autres verticales n'auront qu'à ajouter `current_user: User = Depends(get_current_user)` dans leurs routes.

**`controller/user_controller.py`** :

| Fonction | Route | Réponse | Erreurs |
| --- | --- | --- | --- |
| `create_user` | `POST /users` | `UserReadModel`, code 201 | 409 pseudo ou email pris |
| `login` | `POST /login` | `TokenModel` | 401 identifiants faux |
| `logout` | `POST /logout` | 204 | 401 |
| `read_me` | `GET /users/me` | `UserReadModel` | 401 |
| `update_me` | `PUT /users/me` | `UserReadModel` | 409 email pris |
| `change_password` | `PUT /users/me/password` | 204 | 400 ancien mot de passe faux |
| `delete_me` | `DELETE /users/me` | 204 | 401 |
| `user_by_id` (existe) | `GET /users/{user_id}` | `UserPublicModel` | 404 |
| `search_users` | `GET /users?username=` | `list[UserPublicModel]` | aucune |

Deux points pratiques :

- Les routes `/users/me` doivent être déclarées **avant** `/users/{user_id}`. Sinon FastAPI essaie de lire « me » comme un entier et renvoie une erreur 422.
- La route actuelle `find_all_users` (`GET /users`) renvoie tous les comptes : elle peut être remplacée par la recherche, qui occupe la même URL avec un paramètre.

## Tests prioritaires

Tests du DAO, sur le schéma de test :

- [ ] `login` : bon pseudo et bon hash renvoient l'utilisateur ; mauvais hash renvoie `None` ; pseudo inconnu renvoie `None`

Tests du service, avec `UserDao` remplacé par un `MagicMock` :

- [ ] `create_account` : succès ; pseudo déjà pris ; email déjà pris ; le mot de passe transmis au DAO est bien haché
- [ ] `login` : succès avec jeton généré ; `UserDao().login` reçoit bien le mot de passe haché ; `None` quand le DAO ne trouve personne
- [ ] `logout` : le jeton est remis à `None`
- [ ] `update_profile` : email déjà utilisé par un autre compte refusé
- [ ] `change_password` : ancien mot de passe faux refusé
- [ ] `get_current_user` : jeton inconnu renvoie 401

## Points de coordination

- **Toute l'équipe** : `get_current_user` et la création de compte avec connexion sont nécessaires au jalon du 16 octobre (créer un compte, se connecter, chercher un livre, l'ajouter). À livrer en priorité, même avant le reste du CRUD.
- **Paul (Follow)** : les compteurs du profil (abonnés, abonnements, livres, critiques, likes reçus) étaient prévus dans sa tranche. À décider ensemble : soit `GET /users/{user_id}` les inclut, soit une route séparée du type `GET /users/{user_id}/stats`.
- **Question ouverte** : connexion par pseudo (dossier d'analyse) ou par email (ancien `Classes_Services.md`) ? Ce plan suit le pseudo, comme le hachage actuel.
