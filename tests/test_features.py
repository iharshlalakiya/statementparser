"""Tests for the UPI narration parser."""

from statementparser.features.upi_parser import parse_upi_narration


class TestUPIParser:
    """Test UPI narration parsing with real-world formats."""

    def test_sbi_upi_with_gpay(self):
        """Parse SBI UPI narration with Google Pay."""
        narration = (
            "UPI-Hari Enterprises-gpay-11244530509@okbizaxis"
            "-UTIB0000553-121864632957-UPI Value Dt 19/04/2026 Ref 121864632957"
        )
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.merchant == "Hari Enterprises"
        assert result.app == "Google Pay"
        assert result.vpa == "11244530509@okbizaxis"
        assert result.ifsc == "UTIB0000553"
        assert result.counterparty_bank == "Axis Bank"
        assert result.upi_ref == "121864632957"

    def test_sbi_upi_phonepe(self):
        """Parse SBI UPI narration with PhonePe VPA."""
        narration = (
            "UPI-KISHAN CHOUDHARY-q148808339@ybl"
            "-YESB0YBUPI-121865008435-UPI Value Dt 19/04/2026 Ref 121865008435"
        )
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.merchant == "KISHAN CHOUDHARY"
        assert result.vpa == "q148808339@ybl"
        assert result.app == "PhonePe"

    def test_sbi_upi_with_phone_in_vpa(self):
        """Parse UPI with phone number in VPA."""
        narration = "UPI-Shop Name-9876543210@ybl-YESB0001234-123456789012-UPI"
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.phone == "9876543210"
        assert result.vpa == "9876543210@ybl"

    def test_sbi_upi_slice_app(self):
        """Parse SBI UPI with Slice app VPA."""
        narration = (
            "UPI-Mr VISHAL VIREN SHAH-6353597964@slc"
            "-CBIN0280499-647696908425-UPI Value Dt 20/04/2026 Ref 647696908425"
        )
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.merchant == "Mr VISHAL VIREN SHAH"
        assert result.vpa == "6353597964@slc"
        assert result.app == "Slice"
        assert result.counterparty_bank == "Central Bank of India"

    def test_non_upi_returns_none(self):
        """Non-UPI narrations should return None."""
        assert parse_upi_narration("NEFT-12345-John Doe") is None
        assert parse_upi_narration("ATM WDL-SBI-Mumbai") is None
        assert parse_upi_narration("") is None

    def test_ach_narration_returns_none(self):
        """ACH narrations should return None."""
        narration = "ACH D- TP ACH PRUDENT-2174489277 Value Dt 20/04/2026 Ref 003447610860"
        assert parse_upi_narration(narration) is None

    def test_hospitality_merchant(self):
        """Parse UPI with hospitality merchant."""
        narration = (
            "UPI-OM SAI HOSPITALITY S-20250423142254@yesbank"
            "-YESB0000728-122078234239-UPI Value Dt 24/04/2026 Ref 122078234239"
        )
        result = parse_upi_narration(narration)
        assert result is not None
        assert result.merchant is not None
        assert "HOSPITALITY" in result.merchant.upper() or "OM SAI" in result.merchant.upper()


class TestNormalizer:
    """Test payment method detection."""

    def test_upi_detection(self):
        from statementparser.core.models import PaymentMethod
        from statementparser.features.normalizer import detect_payment_method

        assert detect_payment_method("UPI-Someone-vpa@ybl") == PaymentMethod.UPI
        assert detect_payment_method("NEFT-123-Name") == PaymentMethod.NEFT
        assert detect_payment_method("ATM WDL SBI MUMBAI") == PaymentMethod.ATM
        assert detect_payment_method("ACH D- TP ACH PRUDENT") == PaymentMethod.ACH


class TestCategorizer:
    """Test transaction categorization."""

    def test_food_category(self):
        from statementparser.core.models import TransactionCategory
        from statementparser.features.categorizer import categorize_transaction

        result = categorize_transaction("UPI-ZOMATO-payment", merchant="ZOMATO")
        assert result == TransactionCategory.FOOD

    def test_investment_category(self):
        from statementparser.core.models import TransactionCategory
        from statementparser.features.categorizer import categorize_transaction

        result = categorize_transaction("ACH D- TP ACH PRUDENT-2174489277")
        assert result == TransactionCategory.INVESTMENT

    def test_salary_category(self):
        from statementparser.core.models import TransactionCategory
        from statementparser.features.categorizer import categorize_transaction

        result = categorize_transaction("NEFT-SALARY-Company Name")
        assert result == TransactionCategory.SALARY


class TestBalanceChecker:
    """Test balance verification."""

    def test_valid_balances(self):
        from datetime import date
        from decimal import Decimal

        from statementparser.core.models import Transaction, TransactionType
        from statementparser.features.balance_checker import verify_balances

        txns = [
            Transaction(
                date=date(2026, 4, 19),
                narration="UPI-Test1",
                amount=Decimal("-160"),
                withdrawal=Decimal("160"),
                deposit=Decimal("0"),
                closing_balance=Decimal("28115.82"),
                type=TransactionType.DEBIT,
            ),
            Transaction(
                date=date(2026, 4, 19),
                narration="UPI-Test2",
                amount=Decimal("-20"),
                withdrawal=Decimal("20"),
                deposit=Decimal("0"),
                closing_balance=Decimal("28095.82"),
                type=TransactionType.DEBIT,
            ),
        ]
        result = verify_balances(txns)
        assert result.is_valid is True
        assert len(result.mismatched_rows) == 0

    def test_invalid_balances(self):
        from datetime import date
        from decimal import Decimal

        from statementparser.core.models import Transaction, TransactionType
        from statementparser.features.balance_checker import verify_balances

        txns = [
            Transaction(
                date=date(2026, 4, 19),
                narration="Test1",
                amount=Decimal("-100"),
                withdrawal=Decimal("100"),
                closing_balance=Decimal("1000"),
                type=TransactionType.DEBIT,
            ),
            Transaction(
                date=date(2026, 4, 19),
                narration="Test2",
                amount=Decimal("-50"),
                withdrawal=Decimal("50"),
                closing_balance=Decimal("800"),  # Should be 950
                type=TransactionType.DEBIT,
            ),
        ]
        result = verify_balances(txns)
        assert result.is_valid is False
