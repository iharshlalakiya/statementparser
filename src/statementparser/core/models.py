"""Data models for statementparser.

Defines the core data structures used throughout the library:
- Transaction: A single bank transaction
- UPIDetail: Parsed UPI metadata
- BankInfo: Bank account metadata
- Statement: Complete parsed statement
- BalanceVerification: Result of balance checks
"""

import datetime
from decimal import Decimal
from enum import Enum

import pandas as pd
from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    """Transaction direction."""

    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class PaymentMethod(str, Enum):
    """Payment method extracted from narration."""

    UPI = "UPI"
    NEFT = "NEFT"
    RTGS = "RTGS"
    IMPS = "IMPS"
    ACH = "ACH"
    ATM = "ATM"
    POS = "POS"
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    INTEREST = "INTEREST"
    CHARGE = "CHARGE"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"


class TransactionCategory(str, Enum):
    """Auto-assigned transaction category."""

    FOOD = "Food"
    SHOPPING = "Shopping"
    GROCERIES = "Groceries"
    TRANSPORT = "Transport"
    FUEL = "Fuel"
    RENT = "Rent"
    EMI = "EMI"
    SALARY = "Salary"
    INVESTMENT = "Investment"
    INSURANCE = "Insurance"
    UTILITIES = "Utilities"
    RECHARGE = "Recharge"
    ENTERTAINMENT = "Entertainment"
    MEDICAL = "Medical"
    EDUCATION = "Education"
    TRANSFER = "Transfer"
    ATM_WITHDRAWAL = "ATM Withdrawal"
    INTEREST = "Interest"
    CHARGES = "Charges"
    GOVERNMENT = "Government"
    OTHER = "Other"


class UPIDetail(BaseModel):
    """Parsed UPI transaction metadata.

    Extracted from narration strings like:
    'UPI-Hari Enterprises-gpay-11244530509@okbizaxis-UTIB0000553-121864632957-UPI'
    """

    merchant: str | None = Field(None, description="Merchant or person name")
    app: str | None = Field(None, description="UPI app (Google Pay, PhonePe, Paytm, etc.)")
    vpa: str | None = Field(None, description="Virtual Payment Address (e.g. user@ybl)")
    ifsc: str | None = Field(None, description="IFSC code of counterparty bank")
    upi_ref: str | None = Field(None, description="UPI reference number")
    counterparty_bank: str | None = Field(None, description="Counterparty bank name")
    phone: str | None = Field(None, description="Phone number if present in VPA")


class Transaction(BaseModel):
    """A single bank transaction.

    This is the unified model — same fields regardless of which bank
    the statement came from.
    """

    # Core fields
    date: datetime.date = Field(..., description="Transaction date")
    value_date: datetime.date | None = Field(None, description="Value date (settlement date)")
    narration: str = Field(..., description="Raw narration/description from bank")
    description: str = Field("", description="Cleaned, human-readable description")

    # Amounts
    amount: Decimal = Field(..., description="Signed amount: negative=debit, positive=credit")
    withdrawal: Decimal = Field(Decimal("0"), description="Withdrawal amount (always positive)")
    deposit: Decimal = Field(Decimal("0"), description="Deposit amount (always positive)")
    closing_balance: Decimal | None = Field(None, description="Balance after this transaction")

    # Classification
    type: TransactionType = Field(..., description="DEBIT or CREDIT")
    payment_method: PaymentMethod = Field(
        PaymentMethod.OTHER, description="Payment method (UPI, NEFT, etc.)"
    )
    category: TransactionCategory = Field(
        TransactionCategory.OTHER, description="Auto-categorized transaction type"
    )

    # UPI metadata (populated only for UPI transactions)
    upi: UPIDetail | None = Field(None, description="Parsed UPI metadata")

    # Verification
    balance_verified: bool | None = Field(
        None, description="Whether balance calculation was verified"
    )

    model_config = {"frozen": True}


class BankInfo(BaseModel):
    """Bank account metadata extracted from the statement header."""

    bank_name: str = Field(..., description="Bank name (e.g. 'State Bank of India')")
    bank_code: str = Field(..., description="Bank code (e.g. 'SBI')")
    account_number: str | None = Field(None, description="Account number (masked if partial)")
    ifsc: str | None = Field(None, description="IFSC code")
    branch: str | None = Field(None, description="Branch name")
    account_holder: str | None = Field(None, description="Account holder name")
    address: str | None = Field(None, description="Branch address")


class BalanceVerification(BaseModel):
    """Result of balance verification."""

    is_valid: bool = Field(..., description="Whether all balances check out")
    opening_balance: Decimal | None = Field(None, description="Opening balance")
    closing_balance: Decimal | None = Field(None, description="Final closing balance")
    total_credits: Decimal = Field(Decimal("0"), description="Sum of all deposits")
    total_debits: Decimal = Field(Decimal("0"), description="Sum of all withdrawals")
    expected_closing: Decimal | None = Field(None, description="Calculated closing balance")
    mismatched_rows: list[int] = Field(
        default_factory=list, description="Row indices with balance mismatches"
    )
    error_message: str | None = Field(None, description="Description of verification failure")


class Statement(BaseModel):
    """A fully parsed bank statement.

    Contains all transactions, bank metadata, and verification results.
    This is the primary return type of parse().
    """

    bank: BankInfo = Field(..., description="Bank and account metadata")
    transactions: list[Transaction] = Field(
        default_factory=list, description="List of parsed transactions"
    )
    statement_period: tuple[datetime.date, datetime.date] | None = Field(
        None, description="(start_date, end_date) of the statement"
    )
    balance_verification: BalanceVerification | None = Field(
        None, description="Balance verification result"
    )
    source_file: str = Field("", description="Original file path")
    parse_warnings: list[str] = Field(
        default_factory=list, description="Non-fatal warnings during parsing"
    )

    def to_dataframe(self) -> pd.DataFrame:
        """Convert transactions to a pandas DataFrame.

        Returns:
            DataFrame with unified columns, ready for analysis.
        """
        if not self.transactions:
            return pd.DataFrame()

        records = []
        for txn in self.transactions:
            record = {
                "date": txn.date,
                "value_date": txn.value_date,
                "narration": txn.narration,
                "description": txn.description,
                "amount": float(txn.amount),
                "withdrawal": float(txn.withdrawal),
                "deposit": float(txn.deposit),
                "closing_balance": float(txn.closing_balance) if txn.closing_balance else None,
                "type": txn.type.value,
                "payment_method": txn.payment_method.value,
                "category": txn.category.value,
                "balance_verified": txn.balance_verified,
            }

            # Flatten UPI details
            if txn.upi:
                record["upi_merchant"] = txn.upi.merchant
                record["upi_app"] = txn.upi.app
                record["upi_vpa"] = txn.upi.vpa
                record["upi_ref"] = txn.upi.upi_ref
                record["upi_counterparty_bank"] = txn.upi.counterparty_bank
            else:
                record["upi_merchant"] = None
                record["upi_app"] = None
                record["upi_vpa"] = None
                record["upi_ref"] = None
                record["upi_counterparty_bank"] = None

            records.append(record)

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        if "value_date" in df.columns:
            df["value_date"] = pd.to_datetime(df["value_date"])
        return df

    @property
    def total_credits(self) -> Decimal:
        """Sum of all deposits."""
        return sum((t.deposit for t in self.transactions), Decimal("0"))

    @property
    def total_debits(self) -> Decimal:
        """Sum of all withdrawals."""
        return sum((t.withdrawal for t in self.transactions), Decimal("0"))

    @property
    def net_amount(self) -> Decimal:
        """Net amount (credits - debits)."""
        return self.total_credits - self.total_debits

    @property
    def transaction_count(self) -> int:
        """Total number of transactions."""
        return len(self.transactions)
