"""Tests for document ingestion."""
import pytest
from app.ingestion import IngestionPipeline, Document


class TestIngestionPipeline:
    """Tests for IngestionPipeline class."""

    @pytest.fixture
    def pipeline(self):
        return IngestionPipeline()

    @pytest.mark.asyncio
    async def test_ingest_creates_document(self, pipeline):
        doc = await pipeline.ingest("doc1", "Test Title", "Content here", "manual", {"tag": "test"})
        assert isinstance(doc, Document)
        assert doc.doc_id == "doc1"
        assert doc.title == "Test Title"
        assert doc.content == "Content here"
        assert doc.source == "manual"
        assert doc.metadata == {"tag": "test"}

    @pytest.mark.asyncio
    async def test_ingest_empty_metadata_defaults_to_empty_dict(self, pipeline):
        doc = await pipeline.ingest("doc1", "Title", "Content", "source")
        assert doc.metadata == {}

    @pytest.mark.asyncio
    async def test_ingest_file_txt_decodes_utf8(self, pipeline):
        data = b"Plain text content"
        doc = await pipeline.ingest_file("doc1", "test.txt", data)
        assert doc.content == "Plain text content"
        assert doc.source == "file:txt"

    @pytest.mark.asyncio
    async def test_ingest_file_md_decodes_utf8(self, pipeline):
        data = b"# Markdown\n\nContent"
        doc = await pipeline.ingest_file("doc1", "readme.md", data)
        assert doc.content == "# Markdown\n\nContent"
        assert doc.source == "file:md"

    @pytest.mark.asyncio
    async def test_ingest_file_html_decodes_utf8(self, pipeline):
        data = b"<html><body>HTML</body></html>"
        doc = await pipeline.ingest_file("doc1", "page.html", data)
        assert doc.content == "HTML"
        assert doc.source == "file:html"

    @pytest.mark.asyncio
    async def test_ingest_file_unknown_extension_treated_as_text(self, pipeline):
        data = b"Unknown format"
        doc = await pipeline.ingest_file("doc1", "file.xyz", data)
        assert doc.content == "Unknown format"
        assert doc.source == "file:xyz"

    @pytest.mark.asyncio
    async def test_ingest_file_no_extension(self, pipeline):
        data = b"No extension file"
        doc = await pipeline.ingest_file("doc1", "README", data)
        assert doc.content == "No extension file"
        assert doc.source == "file:readme"

    @pytest.mark.asyncio
    async def test_ingest_file_replaces_invalid_utf8(self, pipeline):
        # Invalid UTF-8 sequence
        data = b"\xff\xfe invalid"
        doc = await pipeline.ingest_file("doc1", "bad.txt", data)
        assert "�" in doc.content  # Replacement character

    @pytest.mark.asyncio
    async def test_ingest_file_pdf_placeholder(self, pipeline):
        # PDF extraction attempted; falls back to raw if extraction fails
        data = b"%PDF-1.4 fake pdf"
        doc = await pipeline.ingest_file("doc1", "doc.pdf", data)
        assert doc.source == "file:pdf"
        # Falls back to raw content when extraction fails
        assert "%PDF" in doc.content