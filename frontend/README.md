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
  app.py            entry point: theme + navigation (visitor pages, or the logged-in pages)
  views/            landing (public home), login, signup, home, discover, library, users, profile,
                    edit_profile, book
  ui/               theme.py (the whole visual identity) and components.py (navbars, hero, cards...)
  auth/session.py   login (POST /login), signup (POST /users), logout (POST /logout + local wipe),
                    account actions (edit profile, change password, delete account)
  api/              one module per backend vertical (routes written here only)
  data/             what the views see: Repository (contract), ApiRepository (real backend),
                    DemoRepository (fictitious data, opt-in), FallbackRepository, factory.py
  utils/            API client (sends `Authorization: Bearer <token>`), logs, settings
  pages/            former template pages (players/game), no longer in the navigation
```

The whole interface is in English. Dark theme: `.streamlit/config.toml` (native Streamlit dark theme, so
that every widget, including dropdown menus, gets light text) + `ui/theme.py` (custom CSS).

### Navigation

* **Visitor**: `landing` (public home), `login`, `signup`. Protected pages are not registered, so a
  logged-out user who opens `/library`, `/profile`... gets the public home.
* **Logged in**: Home, Discover (one search bar: title or author), My Library, Users (search by username),
  Profile (`/profile?user=<id>` = public profile of anyone), Edit Profile, Book.
  Avatar menu: *Edit profile*, *Log out*.

### Backend routes really used

| What | Route |
| --- | --- |
| Log in | `POST /login` `{username, password}` -> `{id_user, username, access_token}` |
| Log out | `POST /logout` (token erased server side), then the whole local session is wiped |
| Create account | `POST /users` `{username, email, password}` -> 201 (409 taken, 422 invalid); no token returned |
| Own account | `GET /users/me`, `GET /users/{id}` (public) |
| Edit profile | `PUT /users/{id}` `{bio?, email?}` (a field left out is unchanged; 403 if not yours; 409 e-mail used) |
| Change password | `PUT /users/{id}/password` `{old_password, new_password}` -> 204 (400 wrong current password) |
| Delete account | `DELETE /users/{id}` -> 204 (403 for someone else's account) |
| Search users | `GET /users?username=<text>` (case-insensitive "contains", public fields only) |
| Public books (visitor home) | `GET /books/find_all/` (no token) |
| Search books | `GET /books/?q=<text>` (needs token; 404 = nothing found) |
| Book details | `GET /books/{work_id}` (needs token; Open Library: subjects, description, editions, average_rating) |
| Library | `POST /readings`, `GET /users/{id}/readings`, `PATCH /readings/{id}`, `DELETE /readings/{id}` |
| Follows | `GET /users/{id}/followers`, `GET /users/{id}/following`, `POST`/`DELETE /users/{id}/follow` |
| Reviews / likes | `/review/books/{work_id}/reviews`, `/review/readings/{id}/review`, `/review/reviews/{id}`, `/review/users/{id}/reviews`, `/review/reviews/{id}/like` |

**Why not `PUT/DELETE /player/{id_player}`?** Those routes act on the legacy `player` table (`PlayerModel`: no
bio, no authentication, so anyone could edit or delete anyone). Accounts live in `user_table`, which only
the `/users/{id}` routes above update, with the Bearer token checked (403 on another user's id).

Reading statuses are `to read`, `in progress`, `read`, `abandoned`; the same strings are sent to the backend and
displayed (`STATUS_LABELS` in `data/models.py` is the single place to change a label).

### Environment switches

| Variable | Default | Effect |
| --- | --- | --- |
| `BACKEND_URL` | `http://localhost:5000` | URL of the backend |
| `PASSWORD_MIN_LENGTH` | `8` | same variable as the backend, used by the signup and password forms |
| `EXLIBRIS_ENABLE_DEMO_LOGIN` | `false` | `true` adds a one-click demo login (fictitious data, no backend call) |
| `EXLIBRIS_DATA_SOURCE` | `api` | `api`: real backend only, errors are shown; `auto`: sample catalogue if unreachable; `demo`: no API call |
| `EXLIBRIS_BACKEND_REVIEWS` | `true` | `false` hides reviews and likes |
| `EXLIBRIS_DEMO_COVERS` | `remote` | `generated`: never request Open Library covers (offline demo) |

Covers are CSS backgrounds over a neutral placeholder, so a missing or unloadable image never shows as a
broken icon. At rest only the cover is shown; on hover (or always, on touch screens) the title and the author
appear on the cover over a gradient. A browser refresh starts a new Streamlit session: the user logs in again.

### Known backend limitations (at the time of writing)

* `PUT /users/{id}/password` with a too short new password answers **500** (the 422 handler cannot serialize
  the `ValueError`): the frontend validates the length itself (`PASSWORD_MIN_LENGTH`).
* Book search and book details go through Open Library: if it is unreachable the pages show a clear message
  (details fall back to the stored book data). `GET /books/?q=` matches whole words (title + author), not
  arbitrary substrings, and answers 404 when nothing matches.
* Only one token per user: logging in elsewhere invalidates the previous session.

## ⚒️ Debugging & Logs

### Logs

The frontend maintains its own logging system to track user interactions and API communication errors.

- Logs are written to the `frontend/logs/` directory.
- The logging format is configured via `logging_config.yml`.

### Code quality

The **format on save** with [Ruff](https://docs.astral.sh/ruff/) is enabled by default in the workspace (cf. *.vscode/settings.json*).
