"""Normalizer — date, amount, and description normalization.

Also contains payment method detection logic used across parsers.
"""

from __future__ import annotations

from statementparser.core.constants import PAYMENT_METHOD_PATTERNS
from statementparser.core.models import PaymentMethod


def detect_payment_method(narration: str) -> PaymentMethod:
    """Detect payment method from narration text.

    Args:
        narration: Raw narration string.

    Returns:
        Detected PaymentMethod enum value.
    """
    upper = narration.upper().strip()

    for method_name, patterns in PAYMENT_METHOD_PATTERNS.items():
        for pattern in patterns:
            if upper.startswith(pattern) or f" {pattern}" in upper:
                try:
                    return PaymentMethod(method_name)
                except ValueError:
                    continue

    return PaymentMethod.OTHER
