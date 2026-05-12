"""Password handling for encrypted Indian bank statement PDFs.

Most Indian banks (SBI, HDFC, ICICI) encrypt PDF statements with
the customer's date of birth in various formats:
    - DDMMYYYY (most common)
    - DD-MM-YYYY
    - DDMMYY
    - Account number (some banks)
"""

from __future__ import annotations

import re


def generate_password_variants(password: str) -> list[str]:
    """Generate common password variants from a base password.

    Indian banks typically use DOB as the PDF password, but
    different banks use different formats.

    Args:
        password: Base password (e.g. '01011990' or '01-01-1990').

    Returns:
        List of password variants to try.
    """
    variants = [password]

    # If it looks like a date, generate variants
    # DDMMYYYY → also try DD-MM-YYYY, DDMMYY, DD/MM/YYYY
    date_match = re.match(r"^(\d{2})[-/]?(\d{2})[-/]?(\d{4})$", password)
    if date_match:
        dd, mm, yyyy = date_match.groups()
        yy = yyyy[2:]
        variants.extend([
            f"{dd}{mm}{yyyy}",      # DDMMYYYY
            f"{dd}-{mm}-{yyyy}",    # DD-MM-YYYY
            f"{dd}/{mm}/{yyyy}",    # DD/MM/YYYY
            f"{dd}{mm}{yy}",        # DDMMYY
            f"{yyyy}{mm}{dd}",      # YYYYMMDD
            f"{dd}.{mm}.{yyyy}",    # DD.MM.YYYY
        ])

    # Remove duplicates while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)

    return unique


def is_common_indian_password(password: str) -> bool:
    """Check if a password looks like a typical Indian bank PDF password.

    Args:
        password: Password string to check.

    Returns:
        True if it matches common DOB patterns.
    """
    # DDMMYYYY
    if re.match(r"^\d{8}$", password):
        return True
    # DD-MM-YYYY or DD/MM/YYYY
    return bool(re.match(r"^\d{2}[-/]\d{2}[-/]\d{4}$", password))
