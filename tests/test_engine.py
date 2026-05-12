"""Tests for the StatementEngine orchestrator."""

from statementparser.core.engine import StatementEngine


class TestStatementEngine:
    def test_engine_init_defaults(self):
        engine = StatementEngine()
        assert engine.categorize is True
        assert engine.verify_balance is True

    def test_engine_init_custom(self):
        engine = StatementEngine(categorize=False, verify_balance=False)
        assert engine.categorize is False
        assert engine.verify_balance is False

    def test_parse_file_not_found(self):
        import pytest

        engine = StatementEngine()
        with pytest.raises(FileNotFoundError):
            engine.parse("nonexistent_file.pdf")

    def test_parse_folder_not_directory(self):
        import pytest

        engine = StatementEngine()
        with pytest.raises(NotADirectoryError):
            engine.parse_folder("nonexistent_folder")
