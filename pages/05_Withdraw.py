import streamlit as st
from utils.ui import require_login, logout_button
from utils.csv_store import ensure_data_files, list_accounts, record_transaction

st.set_page_config(page_title='Withdraw', page_icon='🏧')
ensure_data_files()
require_login()

st.title('🏧 Withdraw')
logout_button()

accounts = list_accounts()
if accounts.empty:
    st.info('No accounts exist. Create one first.')
    st.stop()

accounts['label'] = accounts.apply(lambda r: f"{r['account_no']} — {r['account_type']} — Balance: ₹{float(r['balance']):.2f}", axis=1)
selected_label = st.selectbox('Select account', options=accounts['label'])
row = accounts[accounts['label']==selected_label].iloc[0]
acc_id = int(row['account_id'])
current_balance = float(row['balance'])

amount = st.number_input('Amount to withdraw (₹)', min_value=0.0, step=100.0)
note = st.text_input('Note (optional)')

if st.button('Withdraw'):
    try:
        if amount <= 0:
            st.error('Amount must be greater than 0.')
        elif amount > current_balance:
            st.error('Insufficient balance.')
        else:
            txn = record_transaction(acc_id, 'WITHDRAW', float(amount), note=note)
            st.success(f"Withdrew ₹{amount:.2f}. New balance: ₹{txn['balance_after']:.2f}")
    except Exception as e:
        st.error(f"Withdrawal failed: {e}")
