"""Tests for bank auto-detection."""

import pytest

from statementparser.core.detector import detect_bank
from statementparser.core.exceptions import UnsupportedBankError


class TestBankDetector:
    def test_detect_sbi(self):
        text = "State Bank of India\nAccount Statement\nSBIN0001234"
        assert detect_bank(text) == "SBI"

    def test_detect_hdfc(self):
        text = "HDFC Bank Ltd\nStatement of Account\nhdfcbank.com"
        assert detect_bank(text) == "HDFC"

    def test_detect_icici(self):
        text = "ICICI Bank\nTransaction Statement\nicicibank.com"
        assert detect_bank(text) == "ICICI"

    def test_detect_axis(self):
        text = "Axis Bank\nAccount Statement\naxisbank.com"
        assert detect_bank(text) == "AXIS"

    def test_unsupported_bank(self):
        with pytest.raises(UnsupportedBankError):
            detect_bank("Some random text with no bank info")
