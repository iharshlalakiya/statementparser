"""Tests for ICICI parser."""

from statementparser.parsers.icici import ICICIParser


class TestICICIParser:
    def test_bank_name(self):
        parser = ICICIParser()
        assert parser.bank_name == "ICICI Bank"
        assert parser.bank_code == "ICICI"

    def test_extract_account_info(self):
        text = "ICICI Bank\nAccount Number: 12345678901234\nIFSC: ICIC0001234\n"
        parser = ICICIParser()
        info = parser.extract_account_info(text)
        assert info.bank_code == "ICICI"
        assert info.account_number == "12345678901234"
