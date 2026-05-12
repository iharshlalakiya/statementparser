"""CLI tool for statementparser.

Usage:
    bankparse statement.pdf
    bankparse statement.pdf --password dob1990
    bankparse statement.pdf --bank sbi --output result.csv
    bankparse folder/ --password dob1990 --format excel
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
from rich.console import Console
from rich.table import Table

from statementparser.__version__ import __version__
from statementparser.core.engine import StatementEngine
from statementparser.exporters.csv_excel import export_csv, export_excel
from statementparser.exporters.json_export import export_json
from statementparser.exporters.summary import generate_summary

if TYPE_CHECKING:
    from statementparser.core.models import Statement

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="bankparse")
@click.argument("path", required=False)
@click.option("--password", "-p", help="PDF password (usually DOB in DDMMYYYY)")
@click.option("--bank", "-b", help="Force bank: sbi, hdfc, icici, axis")
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["csv", "excel", "json", "table"]),
    default="table",
    help="Output format (default: table)",
)
@click.option("--no-categorize", is_flag=True, help="Disable auto-categorization")
@click.option("--no-verify", is_flag=True, help="Disable balance verification")
@click.pass_context
def main(
    ctx: click.Context,
    path: str | None,
    password: str | None,
    bank: str | None,
    output: str | None,
    fmt: str,
    no_categorize: bool,
    no_verify: bool,
) -> None:
    """🏦 India Bank Parse — Parse Indian bank statements into clean data."""
    if ctx.invoked_subcommand is not None:
        return

    if not path:
        console.print("[bold]🏦 India Bank Parse[/bold]")
        console.print(f"Version: {__version__}")
        console.print("\nUsage: bankparse <file.pdf> [options]")
        console.print("Run [bold]bankparse --help[/bold] for all options.")
        return

    file_path = Path(path)
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        sys.exit(1)

    engine = StatementEngine(
        categorize=not no_categorize,
        verify_balance=not no_verify,
    )

    with console.status("[bold green]Parsing statement..."):
        try:
            if file_path.is_dir():
                statements = engine.parse_folder(str(file_path), password=password, bank=bank)
                console.print(f"\n[green]✓[/green] Parsed {len(statements)} statements")
                for stmt in statements:
                    _display_statement(stmt, fmt, output)
            else:
                stmt = engine.parse(str(file_path), password=password, bank=bank)
                console.print(f"\n[green]✓[/green] Parsed: {stmt.bank.bank_name}")
                _display_statement(stmt, fmt, output)
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
            sys.exit(1)


def _display_statement(
    stmt: Statement,
    fmt: str,
    output: str | None,
) -> None:
    """Display or export a parsed statement."""

    if fmt == "table":
        _print_table(stmt)
    elif fmt == "csv":
        out = output or f"{stmt.bank.bank_code.lower()}_parsed.csv"
        path = export_csv(stmt, out)
        console.print(f"[green]✓[/green] Saved CSV: {path}")
    elif fmt == "excel":
        out = output or f"{stmt.bank.bank_code.lower()}_parsed.xlsx"
        path = export_excel(stmt, out)
        console.print(f"[green]✓[/green] Saved Excel: {path}")
    elif fmt == "json":
        out = output or f"{stmt.bank.bank_code.lower()}_parsed.json"
        path = export_json(stmt, out)
        console.print(f"[green]✓[/green] Saved JSON: {path}")

    # Print summary
    summary = generate_summary(stmt)
    _print_summary(summary)


def _print_table(stmt: Statement) -> None:
    """Print transactions as a rich table."""
    table = Table(title=f"📄 {stmt.bank.bank_name} Statement", show_lines=True)
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Description", style="white", max_width=35)
    table.add_column("Debit", style="red", justify="right")
    table.add_column("Credit", style="green", justify="right")
    table.add_column("Balance", style="yellow", justify="right")
    table.add_column("Category", style="magenta")
    table.add_column("Method", style="blue")

    for txn in stmt.transactions:
        debit = f"₹{float(txn.withdrawal):,.2f}" if txn.withdrawal > 0 else ""
        credit = f"₹{float(txn.deposit):,.2f}" if txn.deposit > 0 else ""
        balance = f"₹{float(txn.closing_balance):,.2f}" if txn.closing_balance else ""
        desc = txn.upi.merchant if txn.upi and txn.upi.merchant else txn.description[:35]

        table.add_row(
            str(txn.date),
            desc,
            debit,
            credit,
            balance,
            txn.category.value,
            txn.payment_method.value,
        )

    console.print(table)


def _print_summary(summary: dict) -> None:
    """Print a summary section."""
    console.print("\n[bold]📊 Summary[/bold]")
    console.print(f"  Transactions: {summary['total_transactions']}")
    console.print(f"  Total Credits: [green]₹{summary['total_credits']:,.2f}[/green]")
    console.print(f"  Total Debits:  [red]₹{summary['total_debits']:,.2f}[/red]")
    console.print(f"  Net Amount:    ₹{summary['net_amount']:,.2f}")

    if summary.get("balance_verified") is not None:
        verified = summary["balance_verified"]
        status = "[green]✓ Verified[/green]" if verified else "[red]✗ Mismatch[/red]"
        console.print(f"  Balance Check: {status}")

    if summary.get("top_merchants"):
        console.print("\n[bold]🏪 Top Merchants[/bold]")
        for merchant, count in summary["top_merchants"][:5]:
            console.print(f"  {merchant}: {count} txns")
