"""Abstract base class for all bank parsers.

Every bank-specific parser (SBI, HDFC, etc.) must inherit from
BaseBankParser and implement the abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from statementparser.core.constants import AMOUNT_STRIP_CHARS, DATE_FORMATS
from statementparser.core.models import BankInfo, Transaction

if TYPE_CHECKING:
    import pdfplumber


class BaseBankParser(ABC):
    """Abstract base class for bank statement parsers.

    Subclasses must implement:
        - bank_name: Human-readable bank name
        - bank_code: Short code (e.g. 'SBI')
        - parse_transactions: Extract transactions from PDF pages
        - extract_account_info: Extract account metadata from header
    """

    @property
    @abstractmethod
    def bank_name(self) -> str:
        """Full bank name (e.g. 'State Bank of India')."""
        ...

    @property
    @abstractmethod
    def bank_code(self) -> str:
        """Short bank code (e.g. 'SBI')."""
        ...

    @abstractmethod
    def parse_transactions(
        self,
        pages: list[pdfplumber.page.Page],
        full_text: str,
    ) -> list[Transaction]:
        """Parse transactions from PDF pages.

        Args:
            pages: List of pdfplumber Page objects.
            full_text: Full extracted text of the PDF.

        Returns:
            List of Transaction objects.
        """
        ...

    @abstractmethod
    def extract_account_info(self, full_text: str) -> BankInfo:
        """Extract account metadata from the statement header.

        Args:
            full_text: Full extracted text of the PDF.

        Returns:
            BankInfo with available fields populated.
        """
        ...

    # ── Shared Utilities ──────────────────────────────────────────────

    def parse_date(self, date_str: str) -> date | None:
        """Try parsing a date string using bank-specific formats.

        Args:
            date_str: Raw date string from the statement.

        Returns:
            Parsed date or None if no format matched.
        """
        from datetime import datetime

        date_str = date_str.strip()
        formats = DATE_FORMATS.get(self.bank_code, DATE_FORMATS["DEFAULT"])

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def clean_amount(self, amount_str: str) -> Decimal:
        """Clean and parse an amount string to Decimal.

        Handles:
            - Comma-separated numbers: '1,500.00' → 1500.00
            - Currency symbols: '₹ 1500' → 1500
            - Empty/dash values: '' or '-' → 0

        Args:
            amount_str: Raw amount string from the statement.

        Returns:
            Decimal amount value (always positive).
        """
        if not amount_str:
            return Decimal("0")

        cleaned = amount_str.strip()

        # Handle empty/dash/nil values
        if cleaned in ("", "-", "--", "nil", "Nil", "NIL", "0.00"):
            return Decimal("0")

        # Remove currency symbols and formatting
        for char in AMOUNT_STRIP_CHARS:
            cleaned = cleaned.replace(char, "")

        # Handle parentheses for negative (some banks use this)
        cleaned = cleaned.strip()
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = cleaned[1:-1]

        # Handle Cr/Dr suffixes
        cleaned = cleaned.replace("Cr", "").replace("Dr", "").replace("CR", "").replace("DR", "")
        cleaned = cleaned.strip()

        try:
            return abs(Decimal(cleaned))
        except InvalidOperation:
            return Decimal("0")
