"""Front-end switches (read from environment variables, with safe defaults).

EXLIBRIS_DATA_SOURCE
    ``auto`` (default): use the backend API; if the catalogue cannot be fetched, fall back to the
    read-only demo catalogue (clearly flagged in the UI).
    ``api``: always use the API, never the demo catalogue.
    ``demo``: never call the API, everything comes from the demo data.

EXLIBRIS_ENABLE_DEMO_LOGIN
    ``false`` (default): only the real login is offered. Set to ``true`` to add a one-click demo
    login (fictitious account and data, no token, no call to the backend) to the login page.

EXLIBRIS_BACKEND_REVIEWS
    ``true`` (default): reviews and likes use the backend routes, which are mounted under the
    ``/review`` prefix (``/review/books/{work_id}/reviews``, ``/review/readings/{id}/review``,
    ``/review/reviews/{id}/like``...). Set to ``false`` to hide them.

EXLIBRIS_DEMO_COVERS
    ``remote`` (default): demo books use Open Library cover URLs (an elegant generated cover is
    shown underneath while loading or if a cover is missing).
    ``generated``: never request remote covers (useful for an offline demonstration).
"""

import os


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def data_source() -> str:
    value = os.getenv("EXLIBRIS_DATA_SOURCE", "auto").strip().lower()
    return value if value in {"auto", "api", "demo"} else "auto"


def demo_login_enabled() -> bool:
    return _flag("EXLIBRIS_ENABLE_DEMO_LOGIN", False)


def demo_covers_mode() -> str:
    value = os.getenv("EXLIBRIS_DEMO_COVERS", "remote").strip().lower()
    return value if value in {"remote", "generated"} else "remote"


def backend_reviews_enabled() -> bool:
    return _flag("EXLIBRIS_BACKEND_REVIEWS", True)
