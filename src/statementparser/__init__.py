"""
India Bank Parse — Parse Indian bank statements into clean DataFrames.

Supports SBI, HDFC, ICICI, and Axis Bank PDF statements with:
- Password-protected PDF handling
- UPI metadata extraction
- Auto transaction categorization
- Balance verification

Usage:
    >>> from statementparser import parse
    >>> df = parse("sbi_statement.pdf", password="dob1990")
    >>> print(df.head())
"""

from statementparser.__version__ import __version__
from statementparser.core.engine import StatementEngine
from statementparser.core.models import Statement, Transaction

__all__ = [
    "Statement",
    "StatementEngine",
    "Transaction",
    "__version__",
    "parse",
    "parse_folder",
]


def parse(
    file_path: str,
    *,
    password: str | None = None,
    bank: str | None = None,
    categorize: bool = True,
    verify_balance: bool = True,
) -> Statement:
    """Parse a single bank statement file.

    Args:
        file_path: Path to the PDF/Excel/CSV bank statement.
        password: Password for encrypted PDFs (common with Indian banks).
        bank: Force a specific bank parser ('sbi', 'hdfc', 'icici', 'axis').
              If None, auto-detects the bank from PDF content.
        categorize: Whether to auto-categorize transactions.
        verify_balance: Whether to verify balance calculations.

    Returns:
        Statement object containing parsed transactions and metadata.

    Raises:
        FileNotFoundError: If the file does not exist.
        UnsupportedBankError: If the bank cannot be detected or is not supported.
        ParseError: If the statement cannot be parsed.
        PasswordRequiredError: If the PDF is encrypted and no password is provided.

    Example:
        >>> from statementparser import parse
        >>> stmt = parse("sbi_april_2026.pdf", password="01011990")
        >>> df = stmt.to_dataframe()
        >>> print(df[['date', 'amount', 'merchant', 'category']].head())
    """
    engine = StatementEngine(
        categorize=categorize,
        verify_balance=verify_balance,
    )
    return engine.parse(file_path, password=password, bank=bank)


def parse_folder(
    folder_path: str,
    *,
    password: str | None = None,
    bank: str | None = None,
    categorize: bool = True,
    verify_balance: bool = True,
) -> list[Statement]:
    """Parse all bank statement files in a folder.

    Args:
        folder_path: Path to folder containing statement files.
        password: Password for encrypted PDFs.
        bank: Force a specific bank parser.
        categorize: Whether to auto-categorize transactions.
        verify_balance: Whether to verify balance calculations.

    Returns:
        List of Statement objects, one per file.
    """
    engine = StatementEngine(
        categorize=categorize,
        verify_balance=verify_balance,
    )
    return engine.parse_folder(folder_path, password=password, bank=bank)
