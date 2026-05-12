.PHONY: install dev test lint format typecheck build publish-test publish clean docs

## Install production dependencies
install:
	uv sync

## Install with dev dependencies
dev:
	uv sync --extra dev

## Run tests
test:
	uv run pytest

## Run linter
lint:
	uv run ruff check src/ tests/

## Auto-format code
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

## Run type checker
typecheck:
	uv run mypy src/

## Build distribution
build:
	uv build

## Publish to TestPyPI
publish-test:
	uv publish --publish-url https://test.pypi.org/legacy/

## Publish to PyPI
publish:
	uv publish

## Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

## Serve docs locally
docs:
	uv run mkdocs serve
