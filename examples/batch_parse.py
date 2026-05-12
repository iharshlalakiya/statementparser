"""Batch parsing example for statementparser."""

from pathlib import Path

from statementparser import parse_folder
from statementparser.exporters.dataframe import merge_statements

# Ensure you have a folder with sample PDFs
STATEMENTS_FOLDER = "./statements"
PASSWORD = "01011990"  # Assuming all use the same password

def main():
    folder = Path(STATEMENTS_FOLDER)
    if not folder.exists() or not folder.is_dir():
        print(f"Please create a directory named '{STATEMENTS_FOLDER}' and place PDF statements inside.")
        return

    print(f"Parsing all statements in {STATEMENTS_FOLDER}...")
    
    # Parse all PDFs in the folder
    statements = parse_folder(str(folder), password=PASSWORD)
    
    print(f"\nSuccessfully parsed {len(statements)} statements.")

    # Merge all parsed statements into a single DataFrame
    print("\nMerging into a single DataFrame...")
    combined_df = merge_statements(statements)
    
    if not combined_df.empty:
        print(f"Total transactions across all statements: {len(combined_df)}")
        
        # Save combined data
        output_file = "all_transactions_combined.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"Saved combined data to {output_file}")
    else:
        print("No transactions found to merge.")

if __name__ == "__main__":
    main()
