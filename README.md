# 🏦 India Bank Parse

[![PyPI version](https://badge.fury.io/py/statementparser.svg)](https://pypi.org/project/statementparser/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/iharshlalakiya/statementparser/actions/workflows/ci.yml/badge.svg)](https://github.com/iharshlalakiya/statementparser/actions)

**Parse Indian bank statements (SBI, HDFC, ICICI, Axis) into clean, unified pandas DataFrames.**

No more manual data entry. No more messy CSVs. Just clean, structured data from your bank PDFs.

---

## ✨ Features

- 🏦 **Multi-bank support** — SBI, HDFC, ICICI, Axis Bank
- 🔐 **Password-protected PDFs** — handles encrypted statements (DOB-based passwords)
- 📊 **Unified DataFrame output** — same columns regardless of bank
- 💳 **UPI metadata extraction** — parse `UPI-ZOMATO-gpay-user@ybl` into structured fields
- 🏷️ **Auto-categorization** — Food, Salary, EMI, Rent, Investment, etc.
- ✅ **Balance verification** — confirms opening + credits - debits = closing
- 📤 **Export to CSV/Excel/JSON** — Tally-ready Excel with summary sheet
- 🖥️ **CLI tool** — `bankparse statement.pdf` from your terminal
- 🔍 **Auto bank detection** — detects which bank from PDF content

## 📦 Installation

```bash
pip install statementparser
```

## 🚀 Quick Start

### Python API

```python
from statementparser import parse

# Parse a statement (auto-detects bank)
stmt = parse("sbi_statement.pdf", password="01011990")

# Get a clean DataFrame
df = stmt.to_dataframe()
print(df[['date', 'amount', 'category', 'upi_merchant', 'upi_app']].head())

# Access structured data
for txn in stmt.transactions:
    print(f"{txn.date} | ₹{txn.amount} | {txn.category.value}")
    if txn.upi:
        print(f"  → {txn.upi.merchant} via {txn.upi.app}")

# Check balance verification
if stmt.balance_verification:
    print(f"Balance verified: {stmt.balance_verification.is_valid}")
```

### CLI

```bash
# Pretty table output
bankparse statement.pdf --password 01011990

# Export to CSV
bankparse statement.pdf -p 01011990 -f csv -o transactions.csv

# Export to Excel (with summary sheet)
bankparse statement.pdf -p 01011990 -f excel

# Parse all PDFs in a folder
bankparse ./statements/ -p 01011990 -f excel

# Force a specific bank parser
bankparse statement.pdf -b sbi -f json
```

## 🏦 Supported Banks

| Bank | Status | Formats |
|------|--------|---------|
| State Bank of India (SBI) | ✅ | PDF |
| HDFC Bank | ✅ | PDF |
| ICICI Bank | ✅ | PDF |
| Axis Bank | ✅ | PDF |

## 💳 UPI Parsing

The library parses UPI narration strings into structured data:

```
Input:  "UPI-Hari Enterprises-gpay-11244530509@okbizaxis-UTIB0000553-121864632957"

Output: {
    "merchant": "Hari Enterprises",
    "app": "Google Pay",           # from "gpay" + @okbizaxis
    "vpa": "11244530509@okbizaxis",
    "counterparty_bank": "Axis Bank",  # from IFSC UTIB
    "upi_ref": "121864632957"
}
```

## 📊 Auto-Categorization

Transactions are automatically tagged:

| Category | Keywords |
|----------|----------|
| Food | Zomato, Swiggy, Restaurant, Hotel |
| Shopping | Amazon, Flipkart, Myntra |
| Investment | Zerodha, Groww, Prudent, SIP |
| Salary | Salary, Payroll |
| EMI | EMI, Loan, Bajaj Finance |
| Transport | Uber, Ola, IRCTC |
| *... and 15+ more* | |

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/iharshlalakiya/statementparser.git
cd statementparser
uv sync --extra dev

# Run tests
uv run pytest

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Build
uv build
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Want to add support for your bank?** Check the [parser guide](docs/contributing.md) — it's easier than you think!