import streamlit as st
import pandas as pd
from datetime import datetime
from utils.ui import require_login, logout_button
from utils.csv_store import ensure_data_files, list_accounts, list_customers, transactions_for_account
from utils.pdf import build_statement_pdf

st.set_page_config(page_title='Statements', page_icon='🧾')
ensure_data_files()
require_login()

st.title('🧾 Account Statement')
logout_button()

accounts = list_accounts()
customers = list_customers()
if accounts.empty:
    st.info('No accounts exist. Create one first.')
    st.stop()

# Build label and map customer name
def cust_name_for(acc_row):
    cid = str(acc_row['customer_id'])
    row = customers[customers['customer_id']==cid]
    return row.iloc[0]['full_name'] if not row.empty else ''

accounts['label'] = accounts.apply(lambda r: f"{r['account_no']} — {cust_name_for(r)}", axis=1)
selected_label = st.selectbox('Select account', accounts['label'])
acc_row = accounts[accounts['label']==selected_label].iloc[0]
acc_id = int(acc_row['account_id'])
acc_no = acc_row['account_no']
customer_name = cust_name_for(acc_row)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('Start date', value=None)
with col2:
    end_date = st.date_input('End date', value=None)

start_iso = start_date.isoformat() if start_date else ''
end_iso = (datetime.combine(end_date, datetime.max.time()).isoformat() if end_date else '')

# Fetch txns
tx = transactions_for_account(acc_id, start_iso, end_iso)
if tx.empty:
    st.info('No transactions in the selected period.')
else:
    show = tx[['created_at','txn_type','amount','balance_after','note']].copy()
    show['created_at'] = show['created_at'].astype(str)
    st.dataframe(show, use_container_width=True)

period_str = ''
if start_iso or end_iso:
    period_str = f"{start_iso or 'beginning'} to {end_iso or 'now'}"

if st.button('Generate PDF'):
    rows = tx.to_dict(orient='records')
    pdf_bytes = build_statement_pdf('Streamlit Bank', acc_no, customer_name, rows, period=period_str)
    st.download_button('Download Statement PDF', data=pdf_bytes, file_name=f'statement_{acc_no}.pdf', mime='application/pdf')
