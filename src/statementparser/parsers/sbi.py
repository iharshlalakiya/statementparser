"""SBI (State Bank of India) statement parser.

Handles the standard SBI PDF statement format with columns:
    Txn Date | Narration | Withdrawals | Deposits | Closing Balance

Narration patterns handled:
    - UPI-{Name}-{VPA}-{IFSC}-{Ref}-UPI Value Dt {date} Ref {ref}
    - NEFT-{ref}-{name}-{bank}
    - ACH D- TP ACH {entity}-{ref} Value Dt {date} Ref {ref}
    - ATM-WDL / POS / CHQ / INT.PAID etc.
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from statementparser.core.models import BankInfo, Transaction, TransactionType
from statementparser.features.normalizer import detect_payment_method
from statementparser.parsers.base import BaseBankParser

if TYPE_CHECKING:
    import pdfplumber


class SBIParser(BaseBankParser):
    """Parser for State Bank of India (SBI) PDF statements."""

    @property
    def bank_name(self) -> str:
        return "State Bank of India"

    @property
    def bank_code(self) -> str:
        return "SBI"

    def parse_transactions(
        self,
        pages: list[pdfplumber.page.Page],
        full_text: str,
    ) -> list[Transaction]:
        """Parse SBI statement transactions from PDF pages.

        Uses pdfplumber's table extraction to handle the tabular format.
        Falls back to text parsing if table extraction fails.
        """
        transactions: list[Transaction] = []

        for page in pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                # Find the header row to identify column positions
                header_idx, col_map = self._find_header(table)
                if header_idx is None:
                    continue

                # Parse each data row after the header
                for row_idx in range(header_idx + 1, len(table)):
                    row = table[row_idx]
                    txn = self._parse_row(row, col_map)
                    if txn is not None:
                        transactions.append(txn)

        return transactions

    def extract_account_info(self, full_text: str) -> BankInfo:
        """Extract SBI account metadata from statement header."""
        account_number = None
        ifsc = None
        branch = None
        account_holder = None

        # Account number pattern
        acc_match = re.search(r"Account\s*(?:No|Number)[:\s]*(\d{10,18})", full_text, re.IGNORECASE)
        if acc_match:
            account_number = acc_match.group(1)

        # IFSC pattern
        ifsc_match = re.search(r"IFSC[:\s]*(SBIN\d{7})", full_text, re.IGNORECASE)
        if ifsc_match:
            ifsc = ifsc_match.group(1)

        # Branch
        branch_match = re.search(r"Branch[:\s]*([^\n]+)", full_text, re.IGNORECASE)
        if branch_match:
            branch = branch_match.group(1).strip()

        # Account holder
        name_match = re.search(
            r"(?:Name|Account\s*Holder)[:\s]*([^\n]+)", full_text, re.IGNORECASE
        )
        if name_match:
            account_holder = name_match.group(1).strip()

        return BankInfo(
            bank_name=self.bank_name,
            bank_code=self.bank_code,
            account_number=account_number,
            ifsc=ifsc,
            branch=branch,
            account_holder=account_holder,
        )

    # ── Private helpers ──────────────────────────────────────────────

    def _find_header(
        self, table: list[list[str | None]]
    ) -> tuple[int | None, dict[str, int]]:
        """Find the header row and map column names to indices.

        Looks for rows containing keywords like 'Txn Date', 'Narration',
        'Withdrawal', 'Deposit', 'Balance'.
        """
        header_keywords = {
            "date": ["txn date", "date", "trans date", "transaction date"],
            "narration": ["narration", "description", "particulars", "details"],
            "withdrawal": ["withdrawal", "debit", "dr", "withdrawals"],
            "deposit": ["deposit", "credit", "cr", "deposits"],
            "balance": ["balance", "closing balance", "closing bal"],
        }

        for idx, row in enumerate(table):
            if row is None:
                continue

            # Check if this row contains enough header keywords
            col_map: dict[str, int] = {}
            for col_name, keywords in header_keywords.items():
                for cell_idx, cell in enumerate(row):
                    cell_lower = (cell or "").strip().lower()
                    if any(kw in cell_lower for kw in keywords):
                        col_map[col_name] = cell_idx
                        break

            # Need at least date, narration, and one amount column
            if "date" in col_map and "narration" in col_map and (
                "withdrawal" in col_map or "deposit" in col_map or "balance" in col_map
            ):
                return idx, col_map

        return None, {}

    def _parse_row(
        self,
        row: list[str | None],
        col_map: dict[str, int],
    ) -> Transaction | None:
        """Parse a single table row into a Transaction."""
        try:
            # Extract date
            date_str = (row[col_map["date"]] or "").strip()
            if not date_str:
                return None

            txn_date = self.parse_date(date_str)
            if txn_date is None:
                return None

            # Extract narration
            narration = (row[col_map.get("narration", 1)] or "").strip()
            if not narration:
                return None

            # Extract amounts
            withdrawal = Decimal("0")
            deposit = Decimal("0")
            closing_balance = None

            if "withdrawal" in col_map and col_map["withdrawal"] < len(row):
                withdrawal = self.clean_amount(row[col_map["withdrawal"]] or "")

            if "deposit" in col_map and col_map["deposit"] < len(row):
                deposit = self.clean_amount(row[col_map["deposit"]] or "")

            if "balance" in col_map and col_map["balance"] < len(row):
                bal_str = row[col_map["balance"]] or ""
                if bal_str.strip():
                    closing_balance = self.clean_amount(bal_str)

            # Skip rows with no amounts (likely continuation rows or subtotals)
            if withdrawal == 0 and deposit == 0:
                return None

            # Determine transaction type and signed amount
            if withdrawal > 0:
                txn_type = TransactionType.DEBIT
                amount = -withdrawal
            else:
                txn_type = TransactionType.CREDIT
                amount = deposit

            # Extract value date from narration if present
            value_date = self._extract_value_date(narration)

            # Detect payment method
            payment_method = detect_payment_method(narration)

            return Transaction(
                date=txn_date,
                value_date=value_date,
                narration=narration,
                description=self._clean_narration(narration),
                amount=amount,
                withdrawal=withdrawal,
                deposit=deposit,
                closing_balance=closing_balance,
                type=txn_type,
                payment_method=payment_method,
            )

        except (IndexError, ValueError, TypeError):
            return None

    def _extract_value_date(self, narration: str) -> date | None:
        """Extract value date from SBI narration string.

        Pattern: 'Value Dt DD/MM/YYYY' or 'Value Dt DD-MM-YYYY'
        """
        match = re.search(
            r"Value\s+Dt\s+(\d{2}[/-]\d{2}[/-]\d{4})", narration, re.IGNORECASE
        )
        if match:
            return self.parse_date(match.group(1))
        return None

    def _clean_narration(self, narration: str) -> str:
        """Clean up narration for human-readable description.

        Removes reference numbers, value dates, and other noise.
        """
        # Remove Value Dt and Ref portions
        cleaned = re.sub(
            r"\s*-?UPI\s+Value\s+Dt\s+\d{2}[/-]\d{2}[/-]\d{4}\s+Ref\s+\d+",
            "",
            narration,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\s*Value\s+Dt\s+\d{2}[/-]\d{2}[/-]\d{4}\s+Ref\s+\d+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return cleaned.strip()
