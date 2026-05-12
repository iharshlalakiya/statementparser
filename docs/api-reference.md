# API Reference

## `parse()`

```python
from statementparser import parse

stmt = parse(
    file_path="statement.pdf",
    password=None,        # PDF password (DOB in DDMMYYYY)
    bank=None,            # Force bank: 'sbi', 'hdfc', 'icici', 'axis'
    categorize=True,      # Auto-categorize transactions
    verify_balance=True,  # Verify balance calculations
)
```

**Returns:** `Statement` object

## `Statement`

| Property | Type | Description |
|----------|------|-------------|
| `bank` | `BankInfo` | Bank and account metadata |
| `transactions` | `list[Transaction]` | Parsed transactions |
| `statement_period` | `tuple[date, date]` | Start and end dates |
| `balance_verification` | `BalanceVerification` | Balance check result |
| `total_credits` | `Decimal` | Sum of all deposits |
| `total_debits` | `Decimal` | Sum of all withdrawals |
| `to_dataframe()` | `DataFrame` | Convert to pandas DataFrame |

## `Transaction`

| Field | Type | Description |
|-------|------|-------------|
| `date` | `date` | Transaction date |
| `narration` | `str` | Raw narration from bank |
| `amount` | `Decimal` | Signed amount (-debit, +credit) |
| `withdrawal` | `Decimal` | Withdrawal amount |
| `deposit` | `Decimal` | Deposit amount |
| `closing_balance` | `Decimal` | Balance after transaction |
| `type` | `TransactionType` | DEBIT or CREDIT |
| `payment_method` | `PaymentMethod` | UPI, NEFT, IMPS, etc. |
| `category` | `TransactionCategory` | Auto-categorized type |
| `upi` | `UPIDetail` | Parsed UPI metadata (if UPI) |
