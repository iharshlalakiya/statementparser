# Contributing to India Bank Parse

Thank you for your interest in contributing! Here's how you can help.

## 🚀 Quick Start

```bash
git clone https://github.com/iharshlalakiya/statementparser.git
cd statementparser
uv sync --extra dev
uv run pytest
```

## 🏦 Adding a New Bank Parser

1. Create `src/statementparser/parsers/your_bank.py`
2. Inherit from `BaseBankParser`
3. Implement `parse_transactions()` and `extract_account_info()`
4. Register in `parsers/registry.py`
5. Add detection patterns in `core/detector.py`
6. Add tests in `tests/test_parsers/`

## 📝 Code Style

- We use **Ruff** for linting and formatting
- Run `uv run ruff format src/ tests/` before committing
- Run `uv run ruff check src/ tests/` to check for issues

## 🧪 Testing

- Write tests for all new features
- Use synthetic/anonymized test data (never commit real bank statements)
- Run `uv run pytest` before submitting PRs

## 📋 Pull Request Process

1. Fork the repo and create a feature branch
2. Make your changes with tests
3. Run lint + tests
4. Submit PR with a clear description
