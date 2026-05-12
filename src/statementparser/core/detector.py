"""Auto-detect which bank a PDF statement belongs to.

Uses keyword patterns, header text, and structural cues to identify
the issuing bank without user input.
"""

from __future__ import annotations

import re

from statementparser.core.constants import SUPPORTED_BANKS
from statementparser.core.exceptions import UnsupportedBankError

# Detection patterns: regex patterns to match in extracted PDF text
# Each bank has multiple patterns to handle different statement formats
_BANK_DETECTION_PATTERNS: dict[str, list[str]] = {
    "SBI": [
        r"state\s+bank\s+of\s+india",
        r"sbi\s+statement",
        r"onlinesbi\.sbi",
        r"sbicap",
        r"sbin\d{7}",  # IFSC pattern
    ],
    "HDFC": [
        r"hdfc\s+bank",
        r"hdfcbank\.com",
        r"hdfc\d{7}",  # IFSC pattern
        r"netbanking\.hdfcbank",
    ],
    "ICICI": [
        r"icici\s+bank",
        r"icicibank\.com",
        r"icic\d{7}",  # IFSC pattern
    ],
    "AXIS": [
        r"axis\s+bank",
        r"axisbank\.com",
        r"utib\d{7}",  # IFSC pattern
        r"axis\s+statement",
    ],
}


def detect_bank(text: str) -> str:
    """Detect which bank the statement belongs to.

    Scans the first ~2000 chars of extracted text for bank-specific patterns.

    Args:
        text: Extracted text content from the PDF (at least first 2 pages).

    Returns:
        Bank code string (e.g. 'SBI', 'HDFC').

    Raises:
        UnsupportedBankError: If no bank could be identified.
    """
    # Use only first portion of text for detection (header area)
    search_text = text[:3000].lower()

    scores: dict[str, int] = {}

    for bank_code, patterns in _BANK_DETECTION_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            score += len(matches)
        if score > 0:
            scores[bank_code] = score

    if not scores:
        raise UnsupportedBankError(
            f"Could not detect bank from statement text. "
            f"Supported banks: {', '.join(SUPPORTED_BANKS.values())}. "
            f"Use bank='sbi' parameter to force a specific parser."
        )

    # Return bank with highest confidence score
    detected = max(scores, key=lambda k: scores[k])
    return detected


def get_supported_banks() -> dict[str, str]:
    """Return dict of supported bank codes and their full names."""
    return SUPPORTED_BANKS.copy()
