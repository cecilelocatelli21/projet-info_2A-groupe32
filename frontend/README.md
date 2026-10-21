# 🎨 Frontend - Player Dashboard

This is the graphical user interface of the application. It is an interactive web dashboard built with **Streamlit**, designed to consume the backend API.

## 🚀 Run the application

- [ ] Install all dependencies: `uv sync --project frontend --all-extras`

Then you have to be in the *frontend* folder to launch:

- [ ] `cd frontend`
- [ ] `uv run --project . streamlit run src/app.py`


## 🏛️ Architecture (Ex-Libris)

```
src/
  app.py            entry point: theme + navigation (visitor pages, or the 5 pages once logged in)
  views/            landing (public home), login, signup, home, discover, library, profile, book
  ui/               theme.py (the whole visual identity) and components.py (navbars, hero, cards...)
  auth/session.py   real login (POST /login/), real signup (POST /user/users), logout, demo login (off)
  api/              one module per backend vertical (routes written here only)
  data/             what the views see: Repository (contract), ApiRepository (real backend),
                    DemoRepository (fictitious data), FallbackRepository (API + sample catalogue),
                    factory.py (picks the source), search.py (local search/filter/sort)
  utils/            API client (sends `Authorization: Bearer <token>`), logs, settings
  pages/            former template pages (players/game), no longer in the navigation
```

The whole interface is in English.

### Navigation

* **Visitor** (not logged in): `landing` (public home, Netflix-style: hero, shelves of books, call to
  action), `login`, `signup`. Protected pages are not registered, so `/library`, `/profile`... show the
  public home to a logged-out user.
* **Logged in**: `home`, `discover`, `library`, `profile` (`/profile?user=<id>` = public profile of anyone),
  `book`. Log out from the avatar menu: the local session is erased and the visitor home is shown.

### Backend routes really used

| What | Route |
| --- | --- |
| Log in | `POST /login/` body `{username, password}` -> `{id_user, username, access_token}` |
| Create account | `POST /user/users` body `{username, email, password}` -> 201 `{user_id, username, bio, email}` (409 username/email taken, 422 invalid). No token is returned: the user is sent to the login page |
| Public books (visitor home) | `GET /books/find_all/` (no token needed) |
| Search (needs token) | `GET /books/?q=<text>` (`q` required, 404 = nothing found) |
| Book details | `GET /books/{work_id}` |
| Library | `POST /readings`, `GET /users/{id}/readings`, `PATCH /readings/{id}`, `DELETE /readings/{id}` |
| Profile / follows | `GET /user/users/{id}`, `GET /users/{id}/followers`, `GET /users/{id}/following`, `POST`/`DELETE /users/{id}/follow` |
| Reviews / likes | `/review/books/{work_id}/reviews`, `/review/readings/{id}/review`, `/review/reviews/{id}`, `/review/users/{id}/reviews`, `/review/reviews/{id}/like` |

Every protected call sends `Authorization: Bearer <access_token>` (the token is kept in `st.session_state`,
never displayed nor logged; the password is only used for the login / signup call).

### Environment switches

| Variable | Default | Effect |
| --- | --- | --- |
| `BACKEND_URL` | `http://localhost:5000` | URL of the backend |
| `PASSWORD_MIN_LENGTH` | `8` | same variable as the backend, used by the signup form |
| `EXLIBRIS_ENABLE_DEMO_LOGIN` | `false` | `true` adds a one-click demo login (fictitious data, no backend call) |
| `EXLIBRIS_DATA_SOURCE` | `auto` | `auto`: API then sample catalogue if unreachable; `api`: API only; `demo`: no API call |
| `EXLIBRIS_BACKEND_REVIEWS` | `true` | `false` hides reviews and likes |
| `EXLIBRIS_DEMO_COVERS` | `remote` | `generated`: never request Open Library covers (offline demo) |

Covers are CSS backgrounds over a generated cover, so a missing or unloadable image never shows as a
broken icon. A browser refresh starts a new Streamlit session: the user logs in again. The backend has no
`POST /logout` route yet: logging out forgets the token on the front side only.

### Known backend limitations (at the time of writing)

* `POST /user/users` answers 500 because `UserService.create_account` calls `UserDao.find_by_email`, which is
  missing from `user_dao.py`.
* `PATCH /readings/{id}` (change status / rate) answers 500 on a database built from `data/init_db.sql`: the
  materialized view `popular_books` that `ReadingDao.update` refreshes is created nowhere.
* `GET /user/users?username=` answers 500 (`UserService.search` is missing): the user search is not in the navigation.
* The user router is mounted under `/user` in `main.py`, hence `/user/users` instead of the documented `/users`.
* The book search and book details go through Open Library: if it is unreachable the pages show a clear
  message instead of results.

## ⚒️ Debugging & Logs

### Logs

The frontend maintains its own logging system to track user interactions and API communication errors.

- Logs are written to the `frontend/logs/` directory.
- The logging format is configured via `logging_config.yml`.

### Code quality

The **format on save** with [Ruff](https://docs.astral.sh/ruff/) is enabled by default in the workspace (cf. *.vscode/settings.json*).
