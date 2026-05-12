"""Tests for UPI narration parser (dedicated test file)."""

from statementparser.features.upi_parser import parse_upi_narration


class TestUPIParserExtended:
    """Extended UPI parser tests with more edge cases."""

    def test_upi_yesbank_merchant(self):
        narration = (
            "UPI-OM SAI HOSPITALITY S-20250423142254@yesbank"
            "-YESB0000728-122078234239-UPI Value Dt 24/04/2026 Ref 122078234239"
        )
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.vpa is not None
        assert "yesbank" in result.vpa

    def test_minimal_upi(self):
        result = parse_upi_narration("UPI-Someone")
        assert result is not None
        assert result.merchant == "Someone"

    def test_empty_string(self):
        assert parse_upi_narration("") is None

    def test_none_input(self):
        assert parse_upi_narration("") is None
