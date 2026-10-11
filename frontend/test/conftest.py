import pytest
import streamlit as st


@pytest.fixture(autouse=True)
def fresh_session_state(monkeypatch):
    """Streamlit's session_state is replaced by a plain dict-like object for the tests."""

    class State(dict):
        __getattr__ = dict.get

        def __setattr__(self, key, value):
            self[key] = value

    monkeypatch.setattr(st, "session_state", State())
