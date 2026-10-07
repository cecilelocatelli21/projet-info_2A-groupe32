class NotFoundError(Exception):
    """Raised when a requested resource does not exist (mapped to HTTP 404)."""


class ForbiddenError(Exception):
    """Raised when a logged-in user acts on a resource they do not own (mapped to HTTP 403)."""


class ConflictError(Exception):
    """Raised when an action clashes with existing data, e.g. a username already taken (mapped to HTTP 409)."""
