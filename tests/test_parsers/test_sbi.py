"""Tests for SBI parser."""

from statementparser.parsers.sbi import SBIParser


class TestSBIParser:
    def test_bank_name(self):
        parser = SBIParser()
        assert parser.bank_name == "State Bank of India"
        assert parser.bank_code == "SBI"

    def test_parse_date_ddmmyyyy(self):
        parser = SBIParser()
        result = parser.parse_date("19/04/2026")
        assert result is not None
        assert result.day == 19
        assert result.month == 4
        assert result.year == 2026

    def test_clean_amount_comma_separated(self):
        parser = SBIParser()
        from decimal import Decimal
        assert parser.clean_amount("1,500.00") == Decimal("1500.00")
        assert parser.clean_amount("28,115.82") == Decimal("28115.82")

    def test_clean_amount_edge_cases(self):
        parser = SBIParser()
        from decimal import Decimal
        assert parser.clean_amount("") == Decimal("0")
        assert parser.clean_amount("-") == Decimal("0")
        assert parser.clean_amount("0.00") == Decimal("0")

    def test_extract_account_info(self):
        text = (
            "State Bank of India\n"
            "Account Number: 12345678901234\n"
            "IFSC: SBIN0001234\n"
            "Branch: Main Branch Mumbai\n"
        )
        parser = SBIParser()
        info = parser.extract_account_info(text)
        assert info.bank_name == "State Bank of India"
        assert info.account_number == "12345678901234"
        assert info.ifsc == "SBIN0001234"
        assert info.branch == "Main Branch Mumbai"

    def test_find_header(self):
        parser = SBIParser()
        table = [
            ["Txn Date", "Narration", "Withdrawals", "Deposits", "Closing Balance"],
            ["19/04/2026", "UPI-Test", "160.00", "0.00", "28,115.82"],
        ]
        idx, col_map = parser._find_header(table)
        assert idx == 0
        assert "date" in col_map
        assert "narration" in col_map
        assert "withdrawal" in col_map
