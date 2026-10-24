"""Picks the data source for the current session.

* demo session  -> ``DemoRepository`` only (never any API call).
* real session  -> ``ApiRepository``; if the *catalogue* cannot be fetched (or is empty) and the
  settings allow it, the read-only demo catalogue is used and the UI shows a banner.
  Library, status changes and profile always stay on the API: demo and real data are not merged.
"""

from __future__ import annotations

from dataclasses import replace

import streamlit as st

from data.api_repository import ApiRepository
from data.demo_repository import DemoCatalog, DemoRepository
from data.errors import BusinessRuleError, DataUnavailable
from data.repository import Repository
from utils.settings import data_source


class FallbackRepository(ApiRepository):
    """API repository whose catalogue falls back on the demo catalogue when it is unavailable."""

    def __init__(self):
        self._demo = DemoCatalog()
        self.degraded = False
        self.degraded_reason = None

    def _catalog_or_demo(self):
        """Stored books of the server, or None when the sample catalogue must be used instead.

        In ``api`` mode (default) the sample catalogue is never used: an unreachable server raises
        ``DataUnavailable`` (the page says so) and an empty catalogue is simply empty."""
        if data_source() == "demo":
            return None
        try:
            books = super().catalog()
            if books:
                return books
            reason = "The server catalogue is empty."
        except (DataUnavailable, BusinessRuleError) as exc:
            if data_source() == "api":
                raise DataUnavailable(str(exc)) from exc
            reason = f"The server is unreachable or the route is unavailable ({exc})."
        if data_source() == "api":
            return []
        self.degraded, self.degraded_reason = True, reason
        return None

    def catalog(self):
        books = self._catalog_or_demo()
        return self._demo.catalog() if books is None else books

    def featured(self):
        books = self._catalog_or_demo()
        return self._demo.featured() if books is None else books[:4]

    def get_book(self, work_id):
        book = self._demo.get_book(work_id)
        return book or super().get_book(work_id)

    def book_reviews(self, work_id):
        if self._demo.get_book(work_id):  # fictitious reviews: nothing can be recorded on them
            return [replace(r, likeable=False) for r in self._demo.book_reviews(work_id)]
        return super().book_reviews(work_id)


def get_repository() -> Repository:
    if st.session_state.get("mode") == "demo":
        repo = st.session_state.get("_repo_demo")
        if repo is None:
            repo = st.session_state["_repo_demo"] = DemoRepository()
        return repo
    repo = FallbackRepository()
    repo.degraded = False
    return repo
