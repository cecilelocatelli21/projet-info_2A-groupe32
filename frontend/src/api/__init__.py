"""Functions calling the backend, one module per vertical.

Every route used by the pages is written here and only here: if a route changes in the
backend, only this package has to be updated. All functions return the dictionary built
by `utils.api_client`: {"status_code": int, "data": parsed JSON, text, or None}.
"""
