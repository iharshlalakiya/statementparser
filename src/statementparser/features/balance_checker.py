"""Balance verification.

Checks that opening_balance + deposits - withdrawals = closing_balance
for each row, flagging any mismatches.
"""

from __future__ import annotations

from decimal import Decimal

from statementparser.core.models import BalanceVerification, Transaction


def verify_balances(
    transactions: list[Transaction],
    tolerance: Decimal = Decimal("0.01"),
) -> BalanceVerification:
    """Verify balance calculations across all transactions.

    For each consecutive pair of transactions, checks:
        previous_closing - withdrawal + deposit == current_closing

    Args:
        transactions: List of transactions (must be in chronological order).
        tolerance: Acceptable rounding difference (default: ₹0.01).

    Returns:
        BalanceVerification with results.
    """
    if not transactions:
        return BalanceVerification(is_valid=True)

    mismatched_rows: list[int] = []
    total_credits = Decimal("0")
    total_debits = Decimal("0")

    # Calculate totals
    for txn in transactions:
        total_credits += txn.deposit
        total_debits += txn.withdrawal

    # Get opening and closing balances
    first_txn = transactions[0]
    last_txn = transactions[-1]

    opening_balance = None
    closing_balance = last_txn.closing_balance

    # Back-calculate opening balance from first transaction
    if first_txn.closing_balance is not None:
        opening_balance = first_txn.closing_balance + first_txn.withdrawal - first_txn.deposit

    # Verify row-by-row
    for i in range(1, len(transactions)):
        prev = transactions[i - 1]
        curr = transactions[i]

        if prev.closing_balance is None or curr.closing_balance is None:
            continue

        expected = prev.closing_balance - curr.withdrawal + curr.deposit
        actual = curr.closing_balance
        diff = abs(expected - actual)

        if diff > tolerance:
            mismatched_rows.append(i)

    # Calculate expected final closing balance
    expected_closing = None
    if opening_balance is not None:
        expected_closing = opening_balance + total_credits - total_debits

    is_valid = len(mismatched_rows) == 0
    error_message = None
    if not is_valid:
        error_message = (
            f"Balance mismatch found in {len(mismatched_rows)} row(s): rows {mismatched_rows}"
        )

    return BalanceVerification(
        is_valid=is_valid,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_credits=total_credits,
        total_debits=total_debits,
        expected_closing=expected_closing,
        mismatched_rows=mismatched_rows,
        error_message=error_message,
    )
