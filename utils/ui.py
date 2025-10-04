import streamlit as st


def require_login():
    if 'user' not in st.session_state or st.session_state['user'] is None:
        st.error('Please log in to continue.')
        st.stop()


def logout_button():
    if st.button('Logout'):
        st.session_state['user'] = None
        st.success('Logged out')
        st.rerun()