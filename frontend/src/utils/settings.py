"""Front-end switches (read from environment variables, with safe defaults).

EXLIBRIS_DATA_SOURCE
    ``auto`` (default): use the backend API; if the catalogue cannot be fetched, fall back to the
    read-only demo catalogue (clearly flagged in the UI).
    ``api``: always use the API, never the demo catalogue.
    ``demo``: never call the API, everything comes from the demo data.

EXLIBRIS_ENABLE_DEMO_LOGIN
    ``true`` (default) shows the one-click demo login. Set to ``false`` once real authentication
    is ready: the demo mode disappears from the login page.

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
    return _flag("EXLIBRIS_ENABLE_DEMO_LOGIN", True)


def demo_covers_mode() -> str:
    value = os.getenv("EXLIBRIS_DEMO_COVERS", "remote").strip().lower()
    return value if value in {"remote", "generated"} else "remote"
