"""Transaction categorizer.

Auto-categorizes transactions based on narration keywords,
merchant names, and payment method patterns.
"""

from __future__ import annotations

from statementparser.core.constants import CATEGORY_KEYWORDS
from statementparser.core.models import PaymentMethod, TransactionCategory


def categorize_transaction(
    narration: str,
    merchant: str | None = None,
    payment_method: PaymentMethod = PaymentMethod.OTHER,
) -> TransactionCategory:
    """Auto-categorize a transaction based on its narration and metadata.

    Args:
        narration: Raw narration string from the statement.
        merchant: Parsed merchant name (if available).
        payment_method: Detected payment method.

    Returns:
        Best-matching TransactionCategory.
    """
    # Combine narration and merchant for keyword search
    search_text = narration.upper()
    if merchant:
        search_text += " " + merchant.upper()

    # Special cases based on payment method
    if payment_method == PaymentMethod.ATM:
        return TransactionCategory.ATM_WITHDRAWAL
    if payment_method == PaymentMethod.INTEREST:
        return TransactionCategory.INTEREST
    if payment_method == PaymentMethod.CHARGE:
        return TransactionCategory.CHARGES

    # Keyword-based matching with scoring
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.upper() in search_text:
                # Longer keyword matches get higher scores
                score += len(keyword)
        if score > 0:
            scores[category] = score

    if scores:
        best_category = max(scores, key=lambda k: scores[k])
        # Map string back to enum
        for cat in TransactionCategory:
            if cat.value == best_category:
                return cat

    # Default: if it's UPI with no other signal, call it Transfer
    if payment_method == PaymentMethod.UPI:
        return TransactionCategory.TRANSFER

    return TransactionCategory.OTHER
