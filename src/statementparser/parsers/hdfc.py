"""HDFC Bank statement parser."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import TYPE_CHECKING

from statementparser.core.models import BankInfo, Transaction, TransactionType
from statementparser.features.normalizer import detect_payment_method
from statementparser.parsers.base import BaseBankParser

if TYPE_CHECKING:
    import pdfplumber


class HDFCParser(BaseBankParser):
    """Parser for HDFC Bank PDF statements."""

    @property
    def bank_name(self) -> str:
        return "HDFC Bank"

    @property
    def bank_code(self) -> str:
        return "HDFC"

    def parse_transactions(
        self,
        pages: list[pdfplumber.page.Page],
        full_text: str,
    ) -> list[Transaction]:
        transactions: list[Transaction] = []
        for page in pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                header_idx, col_map = self._find_header(table)
                if header_idx is None:
                    continue
                for row_idx in range(header_idx + 1, len(table)):
                    txn = self._parse_row(table[row_idx], col_map)
                    if txn is not None:
                        transactions.append(txn)
        return transactions

    def extract_account_info(self, full_text: str) -> BankInfo:
        account_number = None
        ifsc = None
        branch = None
        acc_match = re.search(r"Account\s*(?:No|Number|#)[.:\s]*(\d{10,18})", full_text, re.I)
        if acc_match:
            account_number = acc_match.group(1)
        ifsc_match = re.search(r"IFSC[:\s]*(HDFC\d{7})", full_text, re.I)
        if ifsc_match:
            ifsc = ifsc_match.group(1)
        branch_match = re.search(r"Branch[:\s]*([^\n]+)", full_text, re.I)
        if branch_match:
            branch = branch_match.group(1).strip()
        return BankInfo(
            bank_name=self.bank_name,
            bank_code=self.bank_code,
            account_number=account_number,
            ifsc=ifsc,
            branch=branch,
        )

    def _find_header(self, table: list[list[str | None]]) -> tuple[int | None, dict[str, int]]:
        kw = {
            "date": ["date"],
            "narration": ["narration", "description", "particulars"],
            "withdrawal": ["withdrawal", "debit"],
            "deposit": ["deposit", "credit"],
            "balance": ["balance", "closing balance"],
        }
        for idx, row in enumerate(table):
            if row is None:
                continue
            col_map: dict[str, int] = {}
            for col_name, keywords in kw.items():
                for ci, cell in enumerate(row):
                    if any(k in (cell or "").strip().lower() for k in keywords):
                        col_map[col_name] = ci
                        break
            if "date" in col_map and "narration" in col_map:
                return idx, col_map
        return None, {}

    def _parse_row(self, row: list[str | None], col_map: dict[str, int]) -> Transaction | None:
        try:
            date_str = (row[col_map["date"]] or "").strip()
            if not date_str:
                return None
            txn_date = self.parse_date(date_str)
            if txn_date is None:
                return None
            narration = (row[col_map.get("narration", 1)] or "").strip()
            if not narration:
                return None
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
            if withdrawal == 0 and deposit == 0:
                return None
            txn_type = TransactionType.DEBIT if withdrawal > 0 else TransactionType.CREDIT
            amount = -withdrawal if withdrawal > 0 else deposit
            return Transaction(
                date=txn_date,
                narration=narration,
                description=narration,
                amount=amount,
                withdrawal=withdrawal,
                deposit=deposit,
                closing_balance=closing_balance,
                type=txn_type,
                payment_method=detect_payment_method(narration),
            )
        except (IndexError, ValueError, TypeError):
            return None
