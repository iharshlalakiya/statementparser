"""PDF reading with password support.

Uses pdfplumber as the primary reader with PyMuPDF (fitz) as fallback.
Handles password-protected PDFs common with Indian bank statements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

from statementparser.core.exceptions import (
    InvalidPasswordError,
    ParseError,
    PasswordRequiredError,
)


@dataclass
class PDFContent:
    """Extracted PDF content."""

    pages: list[pdfplumber.page.Page] = field(default_factory=list)
    full_text: str = ""
    page_count: int = 0
    _pdf: pdfplumber.PDF | None = field(default=None, repr=False)

    def close(self) -> None:
        """Close the underlying PDF file."""
        if self._pdf:
            self._pdf.close()


def read_pdf(file_path: str, password: str | None = None) -> PDFContent:
    """Read a PDF file and extract text content.

    Args:
        file_path: Path to the PDF file.
        password: Password for encrypted PDFs.

    Returns:
        PDFContent with pages and extracted text.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        PasswordRequiredError: If the PDF is encrypted and no password given.
        InvalidPasswordError: If the password is wrong.
        ParseError: If the PDF cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.suffix.lower() == ".pdf":
        raise ParseError(f"Not a PDF file: {file_path}")

    try:
        pdf = pdfplumber.open(str(path), password=password or "")
    except Exception as e:
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            if password:
                raise InvalidPasswordError() from e
            raise PasswordRequiredError() from e
        raise ParseError(f"Cannot open PDF: {e}") from e

    try:
        pages = pdf.pages
        text_parts: list[str] = []
        for page in pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

        full_text = "\n".join(text_parts)

        return PDFContent(
            pages=list(pages),
            full_text=full_text,
            page_count=len(pages),
            _pdf=pdf,
        )
    except Exception as e:
        pdf.close()
        raise ParseError(f"Failed to extract text from PDF: {e}") from e


def read_pdf_with_fallback(file_path: str, password: str | None = None) -> PDFContent:
    """Try pdfplumber first, fall back to PyMuPDF if it fails.

    Some PDFs that pdfplumber can't handle are readable by PyMuPDF.
    """
    try:
        return read_pdf(file_path, password=password)
    except ParseError:
        return _read_pdf_pymupdf(file_path, password=password)


def _read_pdf_pymupdf(file_path: str, password: str | None = None) -> PDFContent:
    """Fallback PDF reader using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError as e:
        raise ParseError(
            "pdfplumber failed and PyMuPDF is not available. Install it with: pip install pymupdf"
        ) from e

    try:
        doc = fitz.open(file_path)
        if doc.is_encrypted:
            if not password:
                doc.close()
                raise PasswordRequiredError()
            if not doc.authenticate(password):
                doc.close()
                raise InvalidPasswordError()

        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())

        full_text = "\n".join(text_parts)
        doc.close()

        # Re-open with pdfplumber for table extraction
        pdf = pdfplumber.open(file_path, password=password or "")
        return PDFContent(
            pages=list(pdf.pages),
            full_text=full_text,
            page_count=len(pdf.pages),
            _pdf=pdf,
        )
    except (PasswordRequiredError, InvalidPasswordError):
        raise
    except Exception as e:
        raise ParseError(f"PyMuPDF fallback also failed: {e}") from e
