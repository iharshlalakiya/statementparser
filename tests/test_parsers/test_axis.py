"""Tests for Axis parser."""

from statementparser.parsers.axis import AxisParser


class TestAxisParser:
    def test_bank_name(self):
        parser = AxisParser()
        assert parser.bank_name == "Axis Bank"
        assert parser.bank_code == "AXIS"

    def test_extract_account_info(self):
        text = "Axis Bank\nAccount Number: 12345678901234\nIFSC: UTIB0001234\n"
        parser = AxisParser()
        info = parser.extract_account_info(text)
        assert info.bank_code == "AXIS"
        assert info.ifsc == "UTIB0001234"
