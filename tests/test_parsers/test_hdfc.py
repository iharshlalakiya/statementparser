"""Tests for HDFC parser."""

from statementparser.parsers.hdfc import HDFCParser


class TestHDFCParser:
    def test_bank_name(self):
        parser = HDFCParser()
        assert parser.bank_name == "HDFC Bank"
        assert parser.bank_code == "HDFC"

    def test_parse_date(self):
        parser = HDFCParser()
        result = parser.parse_date("19/04/26")  # HDFC uses DD/MM/YY
        assert result is not None

    def test_extract_account_info(self):
        text = "HDFC Bank\nAccount No. 12345678901234\nIFSC: HDFC0001234\n"
        parser = HDFCParser()
        info = parser.extract_account_info(text)
        assert info.bank_code == "HDFC"
