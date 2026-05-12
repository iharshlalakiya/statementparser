"""UPI narration parser.

Parses UPI transaction strings from Indian bank statements into
structured metadata. Handles various formats:

SBI format:
    UPI-Hari Enterprises-gpay-11244530509@okbizaxis-UTIB0000553-121864632957-UPI
    Value Dt 19/04/2026 Ref 121864632957

Common pattern:
    UPI-{Name}-{VPA}-{IFSC}-{Ref}-UPI
    UPI-{Name}-{App}-{VPA}-{IFSC}-{Ref}-UPI
"""

from __future__ import annotations

import re

from statementparser.core.constants import IFSC_BANK_MAPPING, VPA_APP_MAPPING
from statementparser.core.models import UPIDetail


def parse_upi_narration(narration: str) -> UPIDetail | None:
    """Parse a UPI narration string into structured metadata.

    Args:
        narration: Raw narration string from the bank statement.

    Returns:
        UPIDetail with extracted fields, or None if not a UPI transaction.
    """
    if not narration:
        return None

    # Check if this is a UPI transaction
    upper = narration.upper()
    if not (upper.startswith("UPI") or "UPI-" in upper or "/UPI/" in upper):
        return None

    # Remove trailing "UPI Value Dt ... Ref ..." portion
    clean = re.sub(
        r"\s*-?UPI\s+Value\s+Dt.*$", "", narration, flags=re.IGNORECASE
    ).strip()
    # Also remove standalone "Value Dt..." if present
    clean = re.sub(
        r"\s*Value\s+Dt.*$", "", clean, flags=re.IGNORECASE
    ).strip()

    # Split by hyphen (the standard UPI narration delimiter)
    # UPI-Name-App/VPA-VPA-IFSC-Ref-UPI
    parts = _split_upi_parts(clean)

    if len(parts) < 2:
        return UPIDetail(merchant=narration)

    merchant = None
    app = None
    vpa = None
    ifsc = None
    upi_ref = None
    counterparty_bank = None
    phone = None

    # First part is always "UPI", skip it
    remaining = parts[1:] if parts[0].upper() == "UPI" else parts

    for part in remaining:
        part = part.strip()
        if not part or part.upper() == "UPI":
            continue

        # Detect VPA (contains @)
        if "@" in part and vpa is None:
            vpa = part
            continue

        # Detect IFSC (standard: 4 letters + 7 alphanum, UPI variant: 4 letters + 6-7 alphanum)
        if re.match(r"^[A-Z]{4}\d{7}$", part, re.IGNORECASE) or \
           re.match(r"^[A-Z]{4}0[A-Z0-9]{5,7}$", part, re.IGNORECASE):
            ifsc = part.upper()
            continue

        # Detect reference number (all digits, 10+ chars)
        if re.match(r"^\d{10,}$", part):
            upi_ref = part
            continue

        # Remaining text is likely merchant name or app name
        if merchant is None:
            merchant = part
        elif app is None and len(part) < 20:
            # Short strings after merchant are likely app identifiers
            app = part

    # Try to detect app from VPA suffix
    if vpa and app is None:
        app = _detect_app_from_vpa(vpa)
    elif app:
        # Normalize known app short names
        app = _normalize_app_name(app)

    # Detect counterparty bank from IFSC
    if ifsc:
        prefix = ifsc[:4].upper()
        counterparty_bank = IFSC_BANK_MAPPING.get(prefix)

    # Extract phone number from VPA if present
    if vpa:
        phone_match = re.match(r"(\d{10})@", vpa)
        if phone_match:
            phone = phone_match.group(1)

    return UPIDetail(
        merchant=merchant,
        app=app,
        vpa=vpa,
        ifsc=ifsc,
        upi_ref=upi_ref,
        counterparty_bank=counterparty_bank,
        phone=phone,
    )


def _split_upi_parts(text: str) -> list[str]:
    """Smart split that handles VPAs containing hyphens.

    VPAs follow pattern: something@something (e.g. user@ybl, 1234@okbizaxis).
    The VPA ends at the first hyphen after the @domain portion.
    """
    # First, find and protect VPAs (pattern: non-hyphen-chars @ non-hyphen-chars)
    # VPA format: localpart@handle where handle doesn't contain hyphens
    vpa_pattern = re.compile(r'[A-Za-z0-9._]+@[A-Za-z0-9]+')

    # Replace VPAs with placeholders to prevent splitting on them
    vpas: list[str] = []
    def _replace_vpa(match: re.Match) -> str:
        vpas.append(match.group())
        return f"__VPA{len(vpas) - 1}__"

    protected = vpa_pattern.sub(_replace_vpa, text)

    # Now split on hyphens
    raw_parts = [p.strip() for p in protected.split("-") if p.strip()]

    # Restore VPAs
    parts: list[str] = []
    for part in raw_parts:
        restored = part
        for i, vpa in enumerate(vpas):
            restored = restored.replace(f"__VPA{i}__", vpa)
        parts.append(restored)

    return parts


def _detect_app_from_vpa(vpa: str) -> str | None:
    """Detect UPI app from VPA suffix."""
    vpa_lower = vpa.lower()
    for suffix, app_name in VPA_APP_MAPPING.items():
        if vpa_lower.endswith(suffix):
            return app_name
    return None


def _normalize_app_name(raw: str) -> str:
    """Normalize short app names to full names."""
    mapping = {
        "gpay": "Google Pay",
        "googlepay": "Google Pay",
        "phonepe": "PhonePe",
        "paytm": "Paytm",
        "bhim": "BHIM",
        "amazonpay": "Amazon Pay",
        "whatsapp": "WhatsApp Pay",
        "cred": "CRED",
        "slice": "Slice",
        "jupiter": "Jupiter",
    }
    return mapping.get(raw.lower(), raw)
