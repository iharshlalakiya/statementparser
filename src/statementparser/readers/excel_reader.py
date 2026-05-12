"""Excel/CSV reader for net banking exports.

Some banks allow downloading statements as Excel (.xlsx) or CSV
from their net banking portals. This reader handles those formats.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from statementparser.core.exceptions import ParseError


def read_excel(file_path: str) -> pd.DataFrame:
    """Read an Excel bank statement export.

    Args:
        file_path: Path to .xlsx or .xls file.

    Returns:
        Raw DataFrame with original columns.

    Raises:
        ParseError: If the file cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        return pd.read_excel(str(path), engine="openpyxl")
    except Exception as e:
        raise ParseError(f"Cannot read Excel file: {e}") from e


def read_csv(file_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    """Read a CSV bank statement export.

    Tries multiple encodings common with Indian bank exports.

    Args:
        file_path: Path to .csv file.
        encoding: File encoding (default: utf-8).

    Returns:
        Raw DataFrame with original columns.

    Raises:
        ParseError: If the file cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try multiple encodings
    encodings = [encoding, "utf-8-sig", "latin-1", "cp1252"]

    for enc in encodings:
        try:
            return pd.read_csv(str(path), encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise ParseError(f"Cannot read CSV file: {e}") from e

    raise ParseError(f"Cannot read CSV file with any supported encoding: {file_path}")
