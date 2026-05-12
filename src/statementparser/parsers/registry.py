"""Parser registry — maps bank codes to parser classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from statementparser.parsers.base import BaseBankParser


def _get_parser_map() -> dict[str, type[BaseBankParser]]:
    """Lazy-load parser classes to avoid circular imports."""
    from statementparser.parsers.axis import AxisParser
    from statementparser.parsers.hdfc import HDFCParser
    from statementparser.parsers.icici import ICICIParser
    from statementparser.parsers.sbi import SBIParser

    return {
        "SBI": SBIParser,
        "HDFC": HDFCParser,
        "ICICI": ICICIParser,
        "AXIS": AxisParser,
    }


def get_parser(bank_code: str) -> BaseBankParser:
    """Get a parser instance for the given bank code.

    Args:
        bank_code: Bank code (e.g. 'SBI', 'HDFC'). Case-insensitive.

    Returns:
        Instantiated parser for the bank.

    Raises:
        ValueError: If the bank code is not supported.
    """
    parser_map = _get_parser_map()
    code = bank_code.upper()

    if code not in parser_map:
        available = ", ".join(sorted(parser_map.keys()))
        raise ValueError(
            f"No parser found for bank '{bank_code}'. Available: {available}"
        )

    return parser_map[code]()


def list_parsers() -> list[str]:
    """Return list of supported bank codes."""
    return sorted(_get_parser_map().keys())
