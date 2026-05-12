"""Tests for exporters."""

from datetime import date
from decimal import Decimal

from statementparser.core.models import (
    BankInfo,
    Statement,
    Transaction,
    TransactionType,
)
from statementparser.exporters.summary import generate_summary


class TestSummary:
    def _make_statement(self) -> Statement:
        return Statement(
            bank=BankInfo(bank_name="State Bank of India", bank_code="SBI"),
            transactions=[
                Transaction(
                    date=date(2026, 4, 19),
                    narration="UPI-ZOMATO-food",
                    amount=Decimal("-160"),
                    withdrawal=Decimal("160"),
                    type=TransactionType.DEBIT,
                ),
                Transaction(
                    date=date(2026, 4, 20),
                    narration="NEFT-SALARY-Company",
                    amount=Decimal("50000"),
                    deposit=Decimal("50000"),
                    type=TransactionType.CREDIT,
                ),
            ],
            statement_period=(date(2026, 4, 19), date(2026, 4, 20)),
        )

    def test_summary_totals(self):
        summary = generate_summary(self._make_statement())
        assert summary["total_transactions"] == 2
        assert summary["total_credits"] == 50000.0
        assert summary["total_debits"] == 160.0

    def test_summary_bank_info(self):
        summary = generate_summary(self._make_statement())
        assert summary["bank"] == "State Bank of India"

    def test_summary_period(self):
        summary = generate_summary(self._make_statement())
        assert summary["period"]["from"] == "2026-04-19"
        assert summary["period"]["to"] == "2026-04-20"
