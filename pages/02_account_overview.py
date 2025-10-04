import streamlit as st
import pandas as pd
from utils.ui import require_login, logout_button
from utils.csv_store import ensure_data_files, read_df, accounts_for_customer, get_customer


st.set_page_config(page_title='Account Overview', page_icon='👤')
ensure_data_files()
require_login()


st.title('👤 Account Overview')
logout_button()


user = st.session_state['user']


# Select a customer (demo support: either linked customer or pick one)
customers = read_df('customers')
if user.get('linked_customer_id'):
    selected_customer_id = str(user['linked_customer_id'])
else:
    if customers.empty:
        st.info('No customers yet. Create one from "Create Account" page.')
        st.stop()
    names = customers[['customer_id','full_name']].astype(str)
    selected = st.selectbox('Select customer', options=names['customer_id'], format_func=lambda cid: names[names['customer_id']==cid]['full_name'].values[0])
    selected_customer_id = selected


cust = get_customer(int(selected_customer_id))
if not cust:
    st.error('Customer not found')
    st.stop()


st.subheader('Customer Details')
st.write({
'Full Name': cust['full_name'],
'Email': cust['email'],
'Phone': cust['phone'],
'Address': cust['address'],
'DOB': cust['dob'],
})


st.subheader('Accounts')
acc_df = accounts_for_customer(int(selected_customer_id))
if acc_df.empty:
    st.info('No accounts for this customer.')
else:
# Convert numeric-looking cols
    if 'balance' in acc_df.columns:
        acc_df['balance'] = pd.to_numeric(acc_df['balance'], errors='coerce').fillna(0.0)
    st.dataframe(acc_df[['account_no','account_type','balance','status','created_at']])