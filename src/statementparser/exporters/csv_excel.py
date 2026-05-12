"""CSV and Excel exporters."""

from __future__ import annotations

from pathlib import Path

from statementparser.core.models import Statement


def export_csv(statement: Statement, output_path: str) -> str:
    """Export statement to CSV file.

    Args:
        statement: Parsed statement.
        output_path: Path for the output CSV file.

    Returns:
        Absolute path of the created file.
    """
    df = statement.to_dataframe()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(path), index=False, encoding="utf-8-sig")  # BOM for Excel compatibility
    return str(path.absolute())


def export_excel(statement: Statement, output_path: str) -> str:
    """Export statement to Excel file with formatting.

    Args:
        statement: Parsed statement.
        output_path: Path for the output Excel file.

    Returns:
        Absolute path of the created file.
    """
    df = statement.to_dataframe()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with __import__("pandas").ExcelWriter(str(path), engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Transactions", index=False)

        # Add summary sheet
        summary_data = {
            "Metric": [
                "Bank",
                "Account",
                "Period",
                "Total Transactions",
                "Total Credits",
                "Total Debits",
                "Net Amount",
            ],
            "Value": [
                statement.bank.bank_name,
                statement.bank.account_number or "N/A",
                (
                    f"{statement.statement_period[0]} to {statement.statement_period[1]}"
                    if statement.statement_period
                    else "N/A"
                ),
                statement.transaction_count,
                f"₹{float(statement.total_credits):,.2f}",
                f"₹{float(statement.total_debits):,.2f}",
                f"₹{float(statement.net_amount):,.2f}",
            ],
        }
        import pandas as pd

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    return str(path.absolute())
