"""Export to Tally-ready format example."""

from pathlib import Path

from statementparser import parse
from statementparser.exporters.csv_excel import export_excel

SAMPLE_PDF = "sample_statement.pdf"
PASSWORD = "01011990"

def main():
    if not Path(SAMPLE_PDF).exists():
        print(f"Please place a valid PDF statement named '{SAMPLE_PDF}' in the current directory.")
        return

    print(f"Parsing {SAMPLE_PDF} for Tally export...")
    stmt = parse(SAMPLE_PDF, password=PASSWORD)

    if not stmt.transactions:
        print("No transactions found.")
        return

    # Export to Excel with a format suitable for accounting software
    # The built-in export_excel function creates a clean sheet with 
    # standardized columns and an optional summary sheet.
    output_file = f"{stmt.bank.bank_code.lower()}_tally_export.xlsx"
    
    print(f"\nGenerating Excel file...")
    saved_path = export_excel(stmt, output_file)
    
    print(f"Successfully exported data to: {saved_path}")
    print("\nThis Excel file can be imported into Tally using standard Excel to XML conversion tools or import utilities.")

if __name__ == "__main__":
    main()
