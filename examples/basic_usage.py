"""Basic usage example for statementparser."""

import json
from pathlib import Path

from statementparser import parse

# Ensure you have a sample PDF to run this script with
SAMPLE_PDF = "sample_statement.pdf"
PASSWORD = "01011990"  # Format: DDMMYYYY

def main():
    if not Path(SAMPLE_PDF).exists():
        print(f"Please place a valid PDF statement named '{SAMPLE_PDF}' in the current directory.")
        return

    print(f"Parsing {SAMPLE_PDF}...")
    
    # Parse the statement
    stmt = parse(SAMPLE_PDF, password=PASSWORD)

    # 1. Print Bank Info
    print("\n--- Bank Information ---")
    print(f"Bank: {stmt.bank.bank_name}")
    print(f"Account: {stmt.bank.account_number}")
    print(f"IFSC: {stmt.bank.ifsc}")

    # 2. Print Summary Statistics
    print("\n--- Summary ---")
    print(f"Total Transactions: {len(stmt.transactions)}")
    print(f"Total Credits: ₹{stmt.total_credits:,.2f}")
    print(f"Total Debits: ₹{stmt.total_debits:,.2f}")
    
    if stmt.balance_verification:
        status = "Verified" if stmt.balance_verification.is_valid else "Mismatch"
        print(f"Balance Check: {status}")

    # 3. Convert to DataFrame and view latest transactions
    df = stmt.to_dataframe()
    if not df.empty:
        print("\n--- Latest Transactions ---")
        print(df[['date', 'description', 'amount', 'category']].tail())

if __name__ == "__main__":
    main()
