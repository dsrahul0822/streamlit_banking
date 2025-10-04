import os
import pandas as pd
from datetime import datetime
from dateutil import tz


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


FILES = {
'users': 'users.csv',
'customers': 'customers.csv',
'accounts': 'accounts.csv',
'transactions': 'transactions.csv',
}


# ---------- Core helpers ----------


def _path(name: str) -> str:
    return os.path.join(DATA_DIR, FILES[name])


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
# Create empty files with headers if missing
    defaults = {
    'users': 'user_id,username,password,linked_customer_id,is_active\n1,admin,admin123,,1\n',
    'customers': 'customer_id,full_name,email,phone,address,dob,created_at\n',
    'accounts': 'account_id,customer_id,account_no,account_type,balance,status,created_at\n',
    'transactions': 'txn_id,account_id,txn_type,amount,balance_after,note,created_at\n',
    }
    for name, fname in FILES.items():
        p = _path(name)
        if not os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as f:
                f.write(defaults[name])


def read_df(name: str) -> pd.DataFrame:
    p = _path(name)
    if not os.path.exists(p):
        ensure_data_files()
    df = pd.read_csv(p, dtype=str).fillna('')
    return df


def write_df(name: str, df: pd.DataFrame):
    p = _path(name)
    df.to_csv(p, index=False)


def _now_iso() -> str:
    return datetime.now(tz.tzlocal()).isoformat(timespec='seconds')


def next_id(df: pd.DataFrame, id_col: str) -> int:
    if df.empty:
        return 1
    try:
        return int(pd.to_numeric(df[id_col], errors='coerce').max()) + 1
    except Exception:
        return 1


# ---------- Auth (demo) ----------


def validate_user(username: str, password: str):
    users = read_df('users')
    row = users[(users['username'] == username) & (users['password'] == password) & (users['is_active'] == '1')]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
    'user_id': int(r['user_id']),
    'username': r['username'],
    'linked_customer_id': int(r['linked_customer_id']) if str(r['linked_customer_id']).strip() else None,
    }



# ---------- Query helpers ----------


def get_customer(customer_id: int):
    customers = read_df('customers')
    row = customers[customers['customer_id'] == str(customer_id)]
    return None if row.empty else row.iloc[0].to_dict()


def accounts_for_customer(customer_id: int) -> pd.DataFrame:
    accounts = read_df('accounts')
    return accounts[accounts['customer_id'] == str(customer_id)]


def get_account_by_no(account_no: str):
    accounts = read_df('accounts')
    row = accounts[accounts['account_no'] == account_no]
    return None if row.empty else row.iloc[0].to_dict()


# ---------- Create operations (used later) ----------


def create_customer(full_name: str, email: str = '', phone: str = '', address: str = '', dob: str = '') -> int:
    customers = read_df('customers')
    cid = next_id(customers, 'customer_id')
    new = {
        'customer_id': cid,
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'address': address,
        'dob': dob,
        'created_at': _now_iso(),
    }
    customers = pd.concat([customers, pd.DataFrame([new])], ignore_index=True)
    write_df('customers', customers)
    return cid

def _generate_account_no(account_id: int) -> str:
    # Simple readable account number: BA-YYYY-XXXX
    year = datetime.now().year
    return f"BA-{year}-{account_id:04d}"


def create_account(customer_id: int, account_type: str = 'SAVINGS', opening_deposit: float = 0.0) -> dict:
    accounts = read_df('accounts')
    aid = next_id(accounts, 'account_id')
    acc_no = _generate_account_no(aid)
    new = {
        'account_id': aid,
        'customer_id': customer_id,
        'account_no': acc_no,
        'account_type': account_type,
        'balance': float(opening_deposit),
        'status': 'ACTIVE',
        'created_at': _now_iso(),
        }
    accounts = pd.concat([accounts, pd.DataFrame([new])], ignore_index=True)
    write_df('accounts', accounts)


    if opening_deposit and float(opening_deposit) > 0:
        record_transaction(aid, 'DEPOSIT', float(opening_deposit), note='Opening deposit')
    return new

def record_transaction(account_id: int, txn_type: str, amount: float, note: str = '') -> dict:
# update balance in accounts and add row in transactions
    accounts = read_df('accounts')
    idx = accounts.index[accounts['account_id'] == str(account_id)]
    if len(idx) == 0:
        raise ValueError('Account not found')
    i = idx[0]


    curr_bal = float(accounts.at[i, 'balance'] or 0.0)
    if txn_type == 'DEPOSIT':
        new_bal = curr_bal + amount
    elif txn_type == 'WITHDRAW':
        if amount > curr_bal:
            raise ValueError('Insufficient balance')
        new_bal = curr_bal - amount
    else:
        raise ValueError('Invalid txn_type')


    accounts.at[i, 'balance'] = new_bal
    write_df('accounts', accounts)


    txns = read_df('transactions')
    tid = next_id(txns, 'txn_id')
    new_txn = {
        'txn_id': tid,
        'account_id': account_id,
        'txn_type': txn_type,
        'amount': float(amount),
        'balance_after': new_bal,
        'note': note,
        'created_at': _now_iso(),
    }
    txns = pd.concat([txns, pd.DataFrame([new_txn])], ignore_index=True)
    write_df('transactions', txns)
    return new_txn

# ---------- Listing helpers ----------

def list_customers() -> pd.DataFrame:
    return read_df('customers')

def list_accounts() -> pd.DataFrame:
    df = read_df('accounts')
    if 'balance' in df.columns:
        df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0.0)
    return df

# ---------- Transactions querying ----------

def transactions_for_account(account_id: int, start_iso: str = '', end_iso: str = '') -> pd.DataFrame:
    tx = read_df('transactions')
    if tx.empty:
        return tx
    tx = tx[tx['account_id'] == str(account_id)].copy()
    if tx.empty:
        return tx
    tx['created_at'] = pd.to_datetime(tx['created_at'], errors='coerce')
    tx = tx.sort_values('created_at')
    if start_iso:
        tx = tx[tx['created_at'] >= pd.to_datetime(start_iso, errors='coerce')]
    if end_iso:
        tx = tx[tx['created_at'] <= pd.to_datetime(end_iso, errors='coerce')]
    tx['amount'] = pd.to_numeric(tx['amount'], errors='coerce').fillna(0.0)
    tx['balance_after'] = pd.to_numeric(tx['balance_after'], errors='coerce').fillna(0.0)
    return tx
