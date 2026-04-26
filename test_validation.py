"""
test_validation.py — Unit tests for file and query validation.

Run with: pytest test_validation.py -v
"""

import pytest
from utils.validator import validate_file, validate_query
import config


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# File Validation Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestValidateFile:
    """Tests for validate_file()."""

    def test_valid_pdf(self):
        ok, err = validate_file("report.pdf", 5_000_000)
        assert ok is True
        assert err is None

    def test_valid_pdf_uppercase_extension(self):
        ok, err = validate_file("report.PDF", 5_000_000)
        assert ok is True
        assert err is None

    def test_invalid_extension_txt(self):
        ok, err = validate_file("notes.txt", 1000)
        assert ok is False
        assert "Unsupported file type" in err

    def test_invalid_extension_docx(self):
        ok, err = validate_file("document.docx", 1000)
        assert ok is False
        assert "Unsupported file type" in err

    def test_file_too_large(self):
        ok, err = validate_file("big.pdf", config.MAX_FILE_SIZE_BYTES + 1)
        assert ok is False
        assert "too large" in err

    def test_file_at_max_size(self):
        ok, err = validate_file("exact.pdf", config.MAX_FILE_SIZE_BYTES)
        assert ok is True
        assert err is None

    def test_empty_file(self):
        ok, err = validate_file("empty.pdf", 0)
        assert ok is False
        assert "empty" in err.lower()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Query Validation Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestValidateQuery:
    """Tests for validate_query()."""

    def test_valid_query(self):
        ok, err = validate_query("What is machine learning?")
        assert ok is True
        assert err is None

    def test_empty_query(self):
        ok, err = validate_query("")
        assert ok is False
        assert "empty" in err.lower()

    def test_whitespace_only_query(self):
        ok, err = validate_query("   ")
        assert ok is False
        assert "empty" in err.lower()

    def test_query_too_short(self):
        ok, err = validate_query("Hi")
        assert ok is False
        assert "too short" in err

    def test_query_at_min_length(self):
        ok, err = validate_query("Why")
        assert ok is True
        assert err is None

    def test_query_too_long(self):
        long_query = "a" * (config.MAX_QUERY_LENGTH + 1)
        ok, err = validate_query(long_query)
        assert ok is False
        assert "too long" in err

    def test_query_at_max_length(self):
        exact_query = "a" * config.MAX_QUERY_LENGTH
        ok, err = validate_query(exact_query)
        assert ok is True
        assert err is None
