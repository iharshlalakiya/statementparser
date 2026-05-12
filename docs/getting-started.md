# Getting Started

## Installation

```bash
pip install statementparser
```

## Basic Usage

```python
from statementparser import parse

# Parse a PDF statement (auto-detects bank)
stmt = parse("sbi_april_2026.pdf", password="01011990")

# Get a pandas DataFrame
df = stmt.to_dataframe()

# View key columns
print(df[['date', 'amount', 'category', 'upi_merchant']].head())
```

## Password-Protected PDFs

Most Indian bank statements are encrypted with your date of birth:

```python
# DOB: 1st January 1990
stmt = parse("statement.pdf", password="01011990")
```

## Force a Specific Bank

```python
stmt = parse("statement.pdf", bank="sbi")
```

## CLI Usage

```bash
bankparse statement.pdf -p 01011990
bankparse statement.pdf -p 01011990 -f csv -o output.csv
bankparse ./statements/ -p 01011990 -f excel
```
