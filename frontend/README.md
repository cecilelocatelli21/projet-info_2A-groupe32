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
  app.py            entry point: theme + navigation (login page, or the 5 pages once logged in)
  views/            login, home (hero + shelves), discover, library, profile, book
  ui/               theme.py (the whole visual identity) and components.py (navbar, hero, cards...)
  auth/session.py   demo login (isolated) and real login (POST /login/), logout
  data/             what the views see: Repository (contract), ApiRepository (real backend),
                    DemoRepository (fictitious data), FallbackRepository (API + demo catalogue),
                    factory.py (picks the source), search.py (local search/filter/sort)
  utils/            API client (unchanged contract), logs, settings (environment switches)
  pages/            former template pages (players/game), no longer in the navigation
```

Views never talk to the API or to the demo data directly: they only use a `Repository`.
Demo and real data are never merged. A demo session only sees demo data (kept in the Streamlit
session, nothing is sent to the backend). The only exception is the read-only *catalogue* fallback
when the API cannot be reached; a banner says so.

### Environment switches

| Variable | Default | Effect |
| --- | --- | --- |
| `EXLIBRIS_ENABLE_DEMO_LOGIN` | `true` | one-click demo login; set `false` once real authentication is ready |
| `EXLIBRIS_DATA_SOURCE` | `auto` | `auto`: API then demo catalogue if unreachable; `api`: API only; `demo`: no API call |
| `EXLIBRIS_DEMO_COVERS` | `remote` | `generated`: never request Open Library covers (offline demo) |

### Public profiles, likes and follows

`views/profile.py` is the only profile page: `/profil` is the connected user, `/profil?user=<id>`
is the public profile of anyone (no follow needed). Usernames (reviews, followers, following) are
buttons calling `ui.open_profile(user_id)`. Likes and the Follow button are independent of what a
profile shows.

Real backend today: profile (`GET /user/{id}`), followers/following, follow/unfollow work.
Not available yet (the front hides or disables them): reviews, likes (no route), account creation
date, and `GET /users/{id}/readings` (see the audit). Set `EXLIBRIS_BACKEND_REVIEWS=true` once the
review/like routes of `doc/Ex-Libris — Endpoints de l'API.md` exist.

### Still to connect (backend side)

- `GET /book/search` (search is local for now), book description/genres/average rating,
  reviews (`/readings/{id}/review`, `/books/{work_id}/reviews`), likes, recommendations.
- The login route currently returns `id_player`; the front accepts it or `user_id`.
- The auth token is sent as `Authorization: Bearer ...` (what the backend expects).

Note: a browser refresh starts a new Streamlit session, so the user must log in again.

## ⚒️ Debugging & Logs

### Logs

The frontend maintains its own logging system to track user interactions and API communication errors.

- Logs are written to the `frontend/logs/` directory.
- The logging format is configured via `logging_config.yml`.

### Code quality

The **format on save** with [Ruff](https://docs.astral.sh/ruff/) is enabled by default in the workspace (cf. *.vscode/settings.json*).
