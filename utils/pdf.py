from fpdf import FPDF
from io import BytesIO

def build_statement_pdf(bank_name: str, account_no: str, cust_name: str, tx_rows: list, period: str = '') -> bytes:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # Header (ASCII only)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, bank_name, ln=1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 6, f'Account Statement - {account_no}', ln=1)  # <-- em dash -> hyphen
    if cust_name:
        pdf.cell(0, 6, f'Customer: {cust_name}', ln=1)
    if period:
        pdf.cell(0, 6, f'Period: {period}', ln=1)
    pdf.ln(4)

    # Table header
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(38, 8, 'Date/Time', border=1)
    pdf.cell(30, 8, 'Type', border=1)
    pdf.cell(40, 8, 'Amount (Rs)', border=1)   # <-- ₹ -> Rs
    pdf.cell(40, 8, 'Balance (Rs)', border=1)  # <-- ₹ -> Rs
    pdf.cell(42, 8, 'Note', border=1, ln=1)

    pdf.set_font('Arial', '', 10)
    for r in tx_rows:
        dt = str(r.get('created_at', ''))[:19]
        t = str(r.get('txn_type', ''))
        try:
            amt = f"{float(r.get('amount', 0)):,.2f}"
        except Exception:
            amt = "0.00"
        try:
            bal = f"{float(r.get('balance_after', 0)):,.2f}"
        except Exception:
            bal = "0.00"
        note = str(r.get('note', ''))
        if len(note) > 28:
            note = note[:27] + '...'   # <-- ellipsis -> three dots
        pdf.cell(38, 8, dt, border=1)
        pdf.cell(30, 8, t, border=1)
        pdf.cell(40, 8, amt, border=1)
        pdf.cell(40, 8, bal, border=1)
        pdf.cell(42, 8, note, border=1, ln=1)

    bio = BytesIO()
    pdf.output(bio)
    return bio.getvalue()
