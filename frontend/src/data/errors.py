"""Errors raised by the data layer and handled by the UI."""


class DataUnavailable(Exception):
    """The data source cannot be reached (API down, timeout, invalid session...)."""


class BusinessRuleError(Exception):
    """The backend (or the demo mirror of it) refused the action because of a business rule."""


class NotFound(BusinessRuleError):
    """HTTP 404: the resource does not exist (for a search: nothing matches)."""
