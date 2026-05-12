"""DataFrame output helper.

Provides utilities for creating and formatting the unified DataFrame output.
"""

from __future__ import annotations

import pandas as pd

from statementparser.core.models import Statement


def to_dataframe(statement: Statement) -> pd.DataFrame:
    """Convert a Statement to a pandas DataFrame.

    This is a convenience function that delegates to Statement.to_dataframe().

    Args:
        statement: Parsed Statement object.

    Returns:
        DataFrame with unified columns.
    """
    return statement.to_dataframe()


def merge_statements(statements: list[Statement]) -> pd.DataFrame:
    """Merge multiple statements into a single DataFrame.

    Useful when parsing a folder of statements from different months.

    Args:
        statements: List of parsed Statement objects.

    Returns:
        Combined DataFrame sorted by date, with a 'source_file' column.
    """
    dfs: list[pd.DataFrame] = []

    for stmt in statements:
        if not stmt.transactions:
            continue
        df = stmt.to_dataframe()
        df["source_file"] = stmt.source_file
        df["bank"] = stmt.bank.bank_name
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.sort_values("date").reset_index(drop=True)
    return combined
