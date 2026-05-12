"""Tests for transaction categorizer (dedicated test file)."""

from statementparser.core.models import PaymentMethod, TransactionCategory
from statementparser.features.categorizer import categorize_transaction


class TestCategorizerExtended:
    def test_shopping_amazon(self):
        result = categorize_transaction("UPI-AMAZON-payment", merchant="AMAZON")
        assert result == TransactionCategory.SHOPPING

    def test_transport_uber(self):
        result = categorize_transaction("UPI-UBER INDIA-payment", merchant="UBER")
        assert result == TransactionCategory.TRANSPORT

    def test_recharge(self):
        result = categorize_transaction("UPI-JIO RECHARGE-payment")
        assert result == TransactionCategory.RECHARGE

    def test_atm_withdrawal_from_method(self):
        result = categorize_transaction(
            "ATM WDL SBI MUMBAI", payment_method=PaymentMethod.ATM
        )
        assert result == TransactionCategory.ATM_WITHDRAWAL

    def test_interest_from_method(self):
        result = categorize_transaction(
            "CR INTEREST", payment_method=PaymentMethod.INTEREST
        )
        assert result == TransactionCategory.INTEREST

    def test_default_upi_is_transfer(self):
        result = categorize_transaction(
            "UPI-RANDOM PERSON-vpa@ybl", payment_method=PaymentMethod.UPI
        )
        assert result == TransactionCategory.TRANSFER

    def test_unknown_is_other(self):
        result = categorize_transaction("SOME UNKNOWN TRANSACTION XYZ123")
        assert result == TransactionCategory.OTHER
