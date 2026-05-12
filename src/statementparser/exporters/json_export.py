"""JSON exporter."""

from __future__ import annotations

import json
from pathlib import Path

from statementparser.core.models import Statement


def export_json(statement: Statement, output_path: str, *, indent: int = 2) -> str:
    """Export statement to JSON file.

    Args:
        statement: Parsed statement.
        output_path: Path for the output JSON file.
        indent: JSON indentation level.

    Returns:
        Absolute path of the created file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(statement.model_dump_json())

    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

    return str(path.absolute())
