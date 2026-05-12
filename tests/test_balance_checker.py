"""Tests for balance checker (dedicated test file)."""

from datetime import date
from decimal import Decimal

from statementparser.core.models import Transaction, TransactionType
from statementparser.features.balance_checker import verify_balances


class TestBalanceCheckerExtended:
    def test_empty_transactions(self):
        result = verify_balances([])
        assert result.is_valid is True

    def test_single_transaction(self):
        txns = [
            Transaction(
                date=date(2026, 4, 19), narration="UPI-Test",
                amount=Decimal("-160"), withdrawal=Decimal("160"),
                closing_balance=Decimal("28115.82"), type=TransactionType.DEBIT,
            ),
        ]
        result = verify_balances(txns)
        assert result.is_valid is True
        assert result.opening_balance == Decimal("28275.82")

    def test_totals_calculation(self):
        txns = [
            Transaction(
                date=date(2026, 4, 19), narration="Debit",
                amount=Decimal("-100"), withdrawal=Decimal("100"),
                closing_balance=Decimal("900"), type=TransactionType.DEBIT,
            ),
            Transaction(
                date=date(2026, 4, 20), narration="Credit",
                amount=Decimal("500"), deposit=Decimal("500"),
                closing_balance=Decimal("1400"), type=TransactionType.CREDIT,
            ),
        ]
        result = verify_balances(txns)
        assert result.total_credits == Decimal("500")
        assert result.total_debits == Decimal("100")
        assert result.is_valid is True

    def test_mismatch_reports_rows(self):
        txns = [
            Transaction(
                date=date(2026, 4, 19), narration="T1",
                amount=Decimal("-100"), withdrawal=Decimal("100"),
                closing_balance=Decimal("1000"), type=TransactionType.DEBIT,
            ),
            Transaction(
                date=date(2026, 4, 20), narration="T2",
                amount=Decimal("-50"), withdrawal=Decimal("50"),
                closing_balance=Decimal("800"),  # Wrong! Should be 950
                type=TransactionType.DEBIT,
            ),
        ]
        result = verify_balances(txns)
        assert result.is_valid is False
        assert 1 in result.mismatched_rows
        assert result.error_message is not None
