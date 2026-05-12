# 🏦 Statement Parser

Parse Indian bank statements (SBI, HDFC, ICICI, Axis) into clean, unified pandas DataFrames.

## Quick Start

```python
from statementparser import parse

stmt = parse("sbi_statement.pdf", password="01011990")
df = stmt.to_dataframe()
print(df.head())
```

## Features

- **Multi-bank support** — SBI, HDFC, ICICI, Axis Bank
- **Password-protected PDFs** — handles encrypted statements
- **UPI metadata extraction** — merchant, app, VPA, bank
- **Auto-categorization** — 20+ transaction categories
- **Balance verification** — row-by-row checks
- **Export** — CSV, Excel (Tally-ready), JSON
- **CLI tool** — `bankparse` command

## Navigation

- [Getting Started](getting-started.md)
- [Supported Banks](supported-banks.md)
- [API Reference](api-reference.md)
- [UPI Parsing](upi-parsing.md)
- [Contributing](contributing.md)
- [Changelog](changelog.md)
