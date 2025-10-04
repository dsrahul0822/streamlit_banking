"""
pages/01_Login.py — Streamlit Banking MVP (CSV-based)
-----------------------------------------------------

What this page does
-------------------
A minimal login screen for the demo banking app. It:
1) Ensures the required CSV files exist (via `ensure_data_files()`).
2) Initializes Streamlit session state so we can remember who is logged in.
3) Shows a login form (username + password).
4) Validates credentials against `data/users.csv` using `validate_user`.
5) On success, stores the user object in `st.session_state['user']` and refreshes the app.
6) If already logged in, it short-circuits and stops the script after showing a message.

Where the data comes from
-------------------------
- `utils/csv_store.ensure_data_files()` creates the CSV files on first run with a demo user:
  data/users.csv  -> contains: user_id, username, password, linked_customer_id, is_active
  Example demo credentials: username = "admin", password = "admin123"

Important concepts
------------------
- `st.session_state`: a persistent dict scoped to the user's browser session.
  We use 'user' key to remember login state across pages.
- `st.form`: groups input widgets so they submit together and run only when the button is pressed.
- `st.rerun()`: forces Streamlit to re-execute the script so the new login state takes effect immediately.

Typical errors & fixes
----------------------
- NameError: 'user' is not defined
  -> Always read/write the logged-in user via st.session_state['user'] (never a bare `user` variable).
- Invalid credentials:
  -> Make sure `data/users.csv` exists (landing page calls ensure_data_files(); this page does too).
  -> Check the row for "admin, admin123" or add your own user rows.

Dependencies
------------
- streamlit
- pandas (transitively used by utils/csv_store)
- Project file: utils/csv_store.py (provides ensure_data_files, validate_user)

Usage
-----
- Start the app with:  streamlit run app.py
- Open this page from the sidebar: "Login"
"""

import streamlit as st
from utils.csv_store import ensure_data_files, validate_user

# Configure Streamlit page (title + icon shown in the browser tab)
st.set_page_config(page_title='Login', page_icon='🔐')

# Ensure the CSV files exist and have the demo user on the first run
ensure_data_files()

# Initialize session state the first time this script runs in this session
# We keep the logged-in user object here so all pages can check auth easily.
if 'user' not in st.session_state:
    st.session_state['user'] = None

st.title('🔐 Login')

# If a user is already stored in session, don't show the form; stop here.
# `st.stop()` prevents the rest of the script from running.
current_user = st.session_state.get('user')
if current_user is not None:
    st.success(f"You are already logged in as {current_user['username']}")
    st.stop()

# A form groups inputs so validation runs only when the submit button is clicked
with st.form('login_form', clear_on_submit=False):
    # Prefill demo credentials for classroom speed; remove defaults for production
    username = st.text_input('Username', value='admin')
    password = st.text_input('Password', type='password', value='admin123')
    submitted = st.form_submit_button('Login')

# Handle form submission
if submitted:
    # Validate against users.csv (returns a dict with user fields or None)
    auth_user = validate_user(username.strip(), password)
    if auth_user is not None:
        # Persist the authenticated user in session so other pages can trust it
        st.session_state['user'] = auth_user
        st.success('Login successful!')
        # Re-run the script so the app immediately reflects the logged-in state
        st.rerun()  # use st.experimental_rerun() if on older Streamlit
    else:
        # Friendly error for wrong username/password or inactive user
        st.error('Invalid credentials or inactive user')
