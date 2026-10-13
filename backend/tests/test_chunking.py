"""Tests for text chunking functionality."""
import pytest
from app.chunking import chunk_text, chunk_semantic


class TestChunkText:
    """Tests for fixed-size chunking."""

    def test_empty_string_returns_empty_list(self):
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert chunk_text("   \n\t  ") == []

    def test_single_chunk_smaller_than_size(self):
        chunks = chunk_text("Hello world", chunk_size=100, chunk_overlap=0)
        assert chunks == ["Hello world"]

    def test_multiple_chunks_no_overlap(self):
        text = "A" * 250
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=0)
        assert len(chunks) == 3
        assert chunks[0] == "A" * 100
        assert chunks[1] == "A" * 100
        assert chunks[2] == "A" * 50

    def test_overlap_between_chunks(self):
        text = "ABCDEFGHIJ"
        chunks = chunk_text(text, chunk_size=5, chunk_overlap=2)
        assert chunks == ["ABCDE", "DEFGH", "GHIJ"]

    def test_overlap_larger_than_chunk_size_raises(self):
        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=10, chunk_overlap=15)

    def test_unicode_text_handling(self):
        text = "你好世界" * 50
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)
        assert len(chunks) > 1
        joined = "".join(chunks)
        assert "你好世界" in joined

    def test_newlines_preserved_in_chunks(self):
        text = "Line 1\nLine 2\nLine 3"
        chunks = chunk_text(text, chunk_size=10, chunk_overlap=2)
        assert any("\n" in c for c in chunks)


class TestChunkSemantic:
    """Tests for semantic (paragraph-based) chunking."""

    def test_empty_string_returns_empty_list(self):
        assert chunk_semantic("") == []

    def test_single_paragraph(self):
        text = "This is a single paragraph with no breaks."
        chunks = chunk_semantic(text)
        assert chunks == [text]

    def test_multiple_paragraphs_split(self):
        text = "Para 1\n\nPara 2\n\nPara 3"
        chunks = chunk_semantic(text)
        assert chunks == ["Para 1", "Para 2", "Para 3"]

    def test_empty_paragraphs_skipped(self):
        text = "Para 1\n\n\n\nPara 2"
        chunks = chunk_semantic(text)
        assert chunks == ["Para 1", "Para 2"]

    def test_long_paragraphs_split_by_size(self):
        long_para = "A" * 1500
        text = f"Short\n\n{long_para}\n\nShort"
        chunks = chunk_semantic(text)
        assert len(chunks) >= 3
        assert "Short" in chunks[0]
        assert "Short" in chunks[-1]

    def test_whitespace_in_paragraphs_trimmed(self):
        text = "  Para 1  \n\n  Para 2  "
        chunks = chunk_semantic(text)
        assert chunks == ["Para 1", "Para 2"]