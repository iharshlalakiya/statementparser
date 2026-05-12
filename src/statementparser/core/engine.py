"""StatementEngine — the main orchestrator.

Coordinates: file reading → bank detection → parsing →
UPI extraction → categorization → balance verification.
"""

from __future__ import annotations

from pathlib import Path

from statementparser.core.detector import detect_bank
from statementparser.core.exceptions import ParseError, UnsupportedBankError
from statementparser.core.models import (
    BankInfo,
    Statement,
    Transaction,
)
from statementparser.features.balance_checker import verify_balances
from statementparser.features.categorizer import categorize_transaction
from statementparser.features.upi_parser import parse_upi_narration
from statementparser.parsers.registry import get_parser
from statementparser.readers.pdf_reader import read_pdf_with_fallback


class StatementEngine:
    """Main engine that orchestrates the full parsing pipeline.

    Pipeline:
        1. Read PDF (with password support)
        2. Auto-detect bank (or use forced bank)
        3. Parse transactions using bank-specific parser
        4. Enrich with UPI metadata
        5. Auto-categorize transactions
        6. Verify balance calculations
    """

    def __init__(
        self,
        *,
        categorize: bool = True,
        verify_balance: bool = True,
    ) -> None:
        self.categorize = categorize
        self.verify_balance = verify_balance

    def parse(
        self,
        file_path: str,
        *,
        password: str | None = None,
        bank: str | None = None,
    ) -> Statement:
        """Parse a single bank statement file.

        Args:
            file_path: Path to the PDF file.
            password: Password for encrypted PDFs.
            bank: Force a specific bank parser (e.g. 'sbi').

        Returns:
            Fully parsed Statement object.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Step 1: Read PDF
        pdf_content = read_pdf_with_fallback(str(path), password=password)

        try:
            # Step 2: Detect bank
            bank_code = bank.upper() if bank else detect_bank(pdf_content.full_text)

            # Step 3: Get parser and parse
            parser = get_parser(bank_code)
            transactions = parser.parse_transactions(pdf_content.pages, pdf_content.full_text)

            if not transactions:
                raise ParseError(
                    "No transactions found. The PDF format may not be supported.",
                    bank=bank_code,
                )

            # Step 4: Extract account info
            bank_info = parser.extract_account_info(pdf_content.full_text)

            # Step 5: Enrich transactions
            enriched = self._enrich_transactions(transactions)

            # Step 6: Build statement
            statement_period = None
            if enriched:
                dates = [t.date for t in enriched]
                statement_period = (min(dates), max(dates))

            # Step 7: Verify balances
            balance_verification = None
            if self.verify_balance:
                balance_verification = verify_balances(enriched)

            return Statement(
                bank=bank_info,
                transactions=enriched,
                statement_period=statement_period,
                balance_verification=balance_verification,
                source_file=str(path.absolute()),
            )

        finally:
            pdf_content.close()

    def parse_folder(
        self,
        folder_path: str,
        *,
        password: str | None = None,
        bank: str | None = None,
    ) -> list[Statement]:
        """Parse all PDF files in a folder.

        Args:
            folder_path: Path to the folder.
            password: Password for encrypted PDFs.
            bank: Force a specific bank parser.

        Returns:
            List of Statement objects (one per file).
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")

        statements: list[Statement] = []
        pdf_files = sorted(folder.glob("*.pdf")) + sorted(folder.glob("*.PDF"))

        for pdf_file in pdf_files:
            try:
                stmt = self.parse(str(pdf_file), password=password, bank=bank)
                statements.append(stmt)
            except (ParseError, UnsupportedBankError) as e:
                # Log warning but continue with other files
                statements.append(
                    Statement(
                        bank=BankInfo(bank_name="Unknown", bank_code="UNKNOWN"),
                        source_file=str(pdf_file),
                        parse_warnings=[str(e)],
                    )
                )

        return statements

    def _enrich_transactions(self, transactions: list[Transaction]) -> list[Transaction]:
        """Enrich transactions with UPI metadata and categories."""
        enriched: list[Transaction] = []

        for txn in transactions:
            upi_detail = parse_upi_narration(txn.narration)

            category = txn.category
            if self.categorize:
                merchant = upi_detail.merchant if upi_detail else None
                category = categorize_transaction(
                    txn.narration, merchant=merchant, payment_method=txn.payment_method
                )

            # Create new transaction with enriched data (models are frozen)
            enriched_txn = Transaction(
                date=txn.date,
                value_date=txn.value_date,
                narration=txn.narration,
                description=txn.description,
                amount=txn.amount,
                withdrawal=txn.withdrawal,
                deposit=txn.deposit,
                closing_balance=txn.closing_balance,
                type=txn.type,
                payment_method=txn.payment_method,
                category=category,
                upi=upi_detail,
                balance_verified=txn.balance_verified,
            )
            enriched.append(enriched_txn)

        return enriched
