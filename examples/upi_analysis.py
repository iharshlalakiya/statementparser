"""UPI analysis example for statementparser."""

import pandas as pd

from statementparser import parse

SAMPLE_PDF = "sample_statement.pdf"
PASSWORD = "01011990"

def main():
    if not pd.io.common.file_exists(SAMPLE_PDF):
        print(f"Please place a valid PDF statement named '{SAMPLE_PDF}' in the current directory.")
        return

    print(f"Analyzing UPI transactions in {SAMPLE_PDF}...")
    stmt = parse(SAMPLE_PDF, password=PASSWORD)
    df = stmt.to_dataframe()

    if df.empty:
        print("No transactions found.")
        return

    # Filter for UPI transactions
    upi_df = df[df['payment_method'] == 'UPI'].copy()
    
    if upi_df.empty:
        print("No UPI transactions found in this statement.")
        return

    print(f"\nFound {len(upi_df)} UPI transactions.")

    # Group by UPI App
    if 'upi_app' in upi_df.columns:
        print("\n--- Usage by UPI App ---")
        app_counts = upi_df['upi_app'].value_counts()
        print(app_counts.to_string())

    # Find top UPI merchants (by amount spent)
    # Debits are negative, so we filter for debits and sum them
    upi_debits = upi_df[upi_df['type'] == 'DEBIT'].copy()
    if not upi_debits.empty and 'upi_merchant' in upi_debits.columns:
        # Make amounts positive for display
        upi_debits.loc[:, 'abs_amount'] = upi_debits['amount'].abs()
        
        print("\n--- Top UPI Merchants (by spend) ---")
        top_merchants = upi_debits.groupby('upi_merchant')['abs_amount'].sum().sort_values(ascending=False).head(5)
        
        for merchant, amount in top_merchants.items():
            print(f"₹{amount:8.2f} - {merchant}")

if __name__ == "__main__":
    main()
