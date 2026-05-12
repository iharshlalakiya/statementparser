"""Summary report generator."""

from __future__ import annotations

from collections import Counter

from statementparser.core.models import Statement


def generate_summary(statement: Statement) -> dict:
    """Generate a summary report of the parsed statement.

    Args:
        statement: Parsed statement.

    Returns:
        Dictionary with summary statistics.
    """
    txns = statement.transactions

    # Category breakdown
    category_counts = Counter(t.category.value for t in txns)
    category_amounts: dict[str, float] = {}
    for t in txns:
        cat = t.category.value
        category_amounts[cat] = category_amounts.get(cat, 0.0) + float(abs(t.amount))

    # Payment method breakdown
    method_counts = Counter(t.payment_method.value for t in txns)

    # Top merchants (from UPI)
    merchants = [t.upi.merchant for t in txns if t.upi and t.upi.merchant]
    merchant_counts = Counter(merchants).most_common(10)

    # UPI app usage
    apps = [t.upi.app for t in txns if t.upi and t.upi.app]
    app_counts = Counter(apps).most_common(10)

    return {
        "bank": statement.bank.bank_name,
        "account": statement.bank.account_number,
        "period": (
            {"from": str(statement.statement_period[0]), "to": str(statement.statement_period[1])}
            if statement.statement_period else None
        ),
        "total_transactions": len(txns),
        "total_credits": float(statement.total_credits),
        "total_debits": float(statement.total_debits),
        "net_amount": float(statement.net_amount),
        "balance_verified": (
            statement.balance_verification.is_valid
            if statement.balance_verification else None
        ),
        "category_breakdown": dict(category_counts.most_common()),
        "category_amounts": category_amounts,
        "payment_methods": dict(method_counts.most_common()),
        "top_merchants": merchant_counts,
        "upi_app_usage": app_counts,
    }
