import streamlit as st
from utils.csv_store import ensure_data_files


st.set_page_config(page_title='Banking MVP', page_icon='🏦', layout='centered')
ensure_data_files()


if 'user' not in st.session_state:
    st.session_state['user'] = None


st.title('🏦 Banking MVP (CSV)')


if st.session_state['user']:
    st.success(f"Logged in as {st.session_state['user']['username']}")
    st.write('Use the sidebar to navigate pages.')
else:
    st.info('Go to **Login** page from the sidebar to sign in. Demo user: **admin / admin123**')


st.caption('Demo app for teaching purposes — data persisted in CSV files.')