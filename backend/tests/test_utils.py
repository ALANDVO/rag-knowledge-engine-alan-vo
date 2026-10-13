"""Tests for utility functions."""
import pytest
from app.utils import (
    generate_id,
    hash_content,
    truncate_text,
    sanitize_filename,
    format_bytes,
    parse_json_safely,
    utc_now_iso,
    merge_metadata,
    extract_keywords,
)


class TestGenerateId:
    def test_generates_unique_ids(self):
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_respects_prefix(self):
        assert generate_id("doc").startswith("doc_")
        assert generate_id("chunk").startswith("chunk_")


class TestHashContent:
    def test_sha256_hash(self):
        result = hash_content("test content", "sha256")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha512_hash(self):
        result = hash_content("test content", "sha512")
        assert len(result) == 128

    def test_deterministic(self):
        h1 = hash_content("same content")
        h2 = hash_content("same content")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = hash_content("content A")
        h2 = hash_content("content B")
        assert h1 != h2


class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("Hi") == "Hi"

    def test_long_text_truncated(self):
        result = truncate_text("A" * 100, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_custom_suffix(self):
        result = truncate_text("Hello World", max_length=8, suffix=">>")
        assert result == "Hello >>"

    def test_exact_length(self):
        result = truncate_text("Hello", max_length=5)
        assert result == "Hello"


    def test_removes_dangerous_chars(self):
        # Input has path separators which get stripped first
        result = sanitize_filename('file<>:"/\\|?*.txt')
        # After path stripping, only the last component remains
        assert result == "___.txt"

    def test_removes_dangerous_chars_no_path(self):
        result = sanitize_filename('doc<>|?*.txt')
        assert result == "doc_____.txt"
    def test_control_chars_removed(self):
        assert sanitize_filename("file\x00\x01.txt") == "file__.txt"

    def test_truncates_long_filename(self):
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255


class TestFormatBytes:
    def test_bytes(self):
        assert format_bytes(500) == "500.0 B"

    def test_kilobytes(self):
        assert format_bytes(1500) == "1.5 KB"

    def test_megabytes(self):
        assert format_bytes(1500000) == "1.4 MB"

    def test_gigabytes(self):
        assert format_bytes(1500000000) == "1.4 GB"


class TestParseJsonSafely:
    def test_valid_json(self):
        assert parse_json_safely('{"key": "value"}') == {"key": "value"}

    def test_invalid_json_returns_default(self):
        assert parse_json_safely("not json", default={"fallback": True}) == {"fallback": True}

    def test_none_returns_default(self):
        assert parse_json_safely(None, default="default") == "default"


class TestMergeMetadata:
    def test_merges_dicts(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_metadata(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_does_not_mutate_base(self):
        base = {"a": 1}
        override = {"b": 2}
        merge_metadata(base, override)
        assert base == {"a": 1}


class TestExtractKeywords:
    def test_extracts_keywords(self):
        text = "The quick brown fox jumps over the lazy dog. The fox is quick."
        keywords = extract_keywords(text, max_keywords=5)
        assert "quick" in keywords
        assert "fox" in keywords
        assert "lazy" in keywords or "dog" in keywords

    def test_respects_max_keywords(self):
        words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
        text = " ".join(words * 20)  # Repeat to increase frequency
        keywords = extract_keywords(text, max_keywords=3)
        assert len(keywords) == 3
        text = "the and for are but not you all any can"
        keywords = extract_keywords(text)
        assert len(keywords) == 0