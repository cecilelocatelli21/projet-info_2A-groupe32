"""
Streamlit page for account registration.

Allows a visitor to create an Ex-Libris account with a username, an email and a password.

Endpoint used:
    POST /users
"""

import os

import streamlit as st

from api import users
from utils.ui import error_detail, init_page

logger = init_page("create_account", "Create an account", "📝", protected=False)

# Same rule as the backend (PASSWORD_MIN_LENGTH), which stays the reference
MIN_PASSWORD_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", 16))

username = st.text_input("Username", max_chars=30)
email = st.text_input("Email")
password = st.text_input("Password", type="password")

is_pwd_long_enough = len(password) >= MIN_PASSWORD_LENGTH
st.write("✅" if is_pwd_long_enough else "❌", f"At least {MIN_PASSWORD_LENGTH} characters")

is_email_valid = "@" in email and "." in email.split("@")[-1]

with st.container(horizontal_alignment="center"):
    if st.button(
        "Create",
        width=150,
        disabled=not (username and is_email_valid and is_pwd_long_enough),
    ):
        logger.info("Create an account")
        response = users.create_account(username, email, password)

        if response["status_code"] in (200, 201):
            logger.info("Account created successfully")
            st.success(f"Account {username} successfully created! 🎉 You can now log in.")
        elif response["status_code"] == 409:
            logger.info("Username or email already taken")
            st.error(f"Username or email already taken: {error_detail(response['data'])}")
        else:
            logger.error(f"Error while creating account: {response}")
            st.error(f"Error: {error_detail(response['data'])}")

if st.button("Back to homepage", type="primary"):
    st.switch_page("pages/home.py")
