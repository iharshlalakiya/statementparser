"""Tests for core models."""

from datetime import date
from decimal import Decimal

from statementparser.core.models import (
    BankInfo,
    Statement,
    Transaction,
    TransactionType,
)


class TestTransaction:
    def test_create_debit(self):
        txn = Transaction(
            date=date(2026, 4, 19),
            narration="UPI-Test",
            amount=Decimal("-160.00"),
            withdrawal=Decimal("160.00"),
            type=TransactionType.DEBIT,
        )
        assert txn.amount == Decimal("-160.00")
        assert txn.type == TransactionType.DEBIT

    def test_create_credit(self):
        txn = Transaction(
            date=date(2026, 4, 20),
            narration="NEFT-Salary",
            amount=Decimal("50000.00"),
            deposit=Decimal("50000.00"),
            type=TransactionType.CREDIT,
        )
        assert txn.amount == Decimal("50000.00")
        assert txn.type == TransactionType.CREDIT


class TestStatement:
    def test_to_dataframe(self):
        stmt = Statement(
            bank=BankInfo(bank_name="State Bank of India", bank_code="SBI"),
            transactions=[
                Transaction(
                    date=date(2026, 4, 19),
                    narration="UPI-Test",
                    amount=Decimal("-160"),
                    withdrawal=Decimal("160"),
                    type=TransactionType.DEBIT,
                ),
            ],
        )
        df = stmt.to_dataframe()
        assert len(df) == 1
        assert df.iloc[0]["amount"] == -160.0

    def test_totals(self):
        stmt = Statement(
            bank=BankInfo(bank_name="SBI", bank_code="SBI"),
            transactions=[
                Transaction(
                    date=date(2026, 4, 19),
                    narration="Debit",
                    amount=Decimal("-100"),
                    withdrawal=Decimal("100"),
                    type=TransactionType.DEBIT,
                ),
                Transaction(
                    date=date(2026, 4, 20),
                    narration="Credit",
                    amount=Decimal("500"),
                    deposit=Decimal("500"),
                    type=TransactionType.CREDIT,
                ),
            ],
        )
        assert stmt.total_debits == Decimal("100")
        assert stmt.total_credits == Decimal("500")
        assert stmt.net_amount == Decimal("400")
        assert stmt.transaction_count == 2
