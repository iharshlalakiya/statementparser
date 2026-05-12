"""Custom exceptions for statementparser."""


class IndiaBankParseError(Exception):
    """Base exception for all statementparser errors."""


class UnsupportedBankError(IndiaBankParseError):
    """Raised when the bank cannot be identified or is not supported."""

    def __init__(self, message: str = "Could not detect bank or bank is not supported.") -> None:
        super().__init__(message)


class ParseError(IndiaBankParseError):
    """Raised when the statement cannot be parsed.

    This typically means the PDF layout doesn't match any known format
    for the detected bank.
    """

    def __init__(
        self,
        message: str = "Failed to parse statement.",
        *,
        bank: str | None = None,
        page: int | None = None,
    ) -> None:
        if bank:
            message = f"[{bank}] {message}"
        if page is not None:
            message = f"{message} (page {page})"
        super().__init__(message)
        self.bank = bank
        self.page = page


class PasswordRequiredError(IndiaBankParseError):
    """Raised when a PDF is password-protected and no password was provided."""

    def __init__(
        self,
        message: str = (
            "PDF is password-protected. "
            "Pass password= parameter (usually your date of birth in DDMMYYYY format)."
        ),
    ) -> None:
        super().__init__(message)


class InvalidPasswordError(IndiaBankParseError):
    """Raised when the provided password is incorrect."""

    def __init__(self, message: str = "Incorrect password for PDF.") -> None:
        super().__init__(message)


class BalanceVerificationError(IndiaBankParseError):
    """Raised when balance verification fails.

    This is a warning-level issue — the statement was parsed but
    the numbers don't add up.
    """

    def __init__(
        self,
        message: str = "Balance verification failed.",
        *,
        mismatched_rows: list[int] | None = None,
    ) -> None:
        super().__init__(message)
        self.mismatched_rows = mismatched_rows or []


class EmptyStatementError(IndiaBankParseError):
    """Raised when the statement contains no transactions."""

    def __init__(self, message: str = "No transactions found in statement.") -> None:
        super().__init__(message)
