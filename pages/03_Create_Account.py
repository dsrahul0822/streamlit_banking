import streamlit as st
from utils.ui import require_login, logout_button
from utils.csv_store import ensure_data_files, list_customers, create_customer, create_account

st.set_page_config(page_title='Create Account', page_icon='➕')
ensure_data_files()
require_login()

st.title('➕ Create Customer & Account')
logout_button()

st.markdown('Use an **existing** customer or create a **new** one.')

with st.form('create_acc_form'):
    mode = st.radio('Customer mode', ['Existing customer', 'New customer'], horizontal=True)

    existing_cid = None
    if mode == 'Existing customer':
        customers = list_customers()
        if customers.empty:
            st.info('No customers found. Switch to **New customer**.')
        else:
            options = customers['customer_id'].astype(str).tolist()
            def _label(cid):
                row = customers[customers['customer_id']==cid].iloc[0]
                return f"{row['full_name']} (ID {cid})"
            existing_cid = st.selectbox('Select customer', options=options, format_func=_label)

    st.subheader('Customer details')
    full_name = st.text_input('Full name')
    email = st.text_input('Email')
    phone = st.text_input('Phone')
    address = st.text_area('Address')
    dob = st.text_input('Date of Birth (YYYY-MM-DD)')

    st.subheader('Account details')
    account_type = st.selectbox('Account type', ['SAVINGS','CURRENT'])
    opening_deposit = st.number_input('Opening deposit', min_value=0.0, step=100.0, value=0.0)

    submitted = st.form_submit_button('Create account')

if submitted:
    try:
        if mode == 'Existing customer' and existing_cid:
            customer_id = int(existing_cid)
        else:
            if not full_name.strip():
                st.error('Full name is required to create a new customer.')
                st.stop()
            customer_id = create_customer(full_name.strip(), email.strip(), phone.strip(), address.strip(), dob.strip())

        acc = create_account(customer_id, account_type, float(opening_deposit))
        st.success(f"Created account {acc['account_no']} for customer ID {customer_id}.")
        st.balloons()
    except Exception as e:
        st.error(f"Failed to create account: {e}")
