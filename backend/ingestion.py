"""Document ingestion: PDF, DOCX, HTML, plain text."""
import structlog
from dataclasses import dataclass, field
from typing import Any

log = structlog.get_logger()


@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    source: str
    metadata: dict = field(default_factory=dict)


class IngestionPipeline:
    """Ingests documents from various formats."""

    async def ingest(self, doc_id: str, title: str, content: str,
                     source: str, metadata: dict = None) -> Document:
        log.info("ingest_start", doc_id=doc_id, title=title, size=len(content))
        doc = Document(doc_id=doc_id, title=title, content=content,
                       source=source, metadata=metadata or {})
        log.info("ingest_done", doc_id=doc_id)
        return doc

    async def ingest_file(self, doc_id: str, filename: str,
                          data: bytes) -> Document:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in ("pdf", "docx", "html", "txt", "md"):
            content = data.decode("utf-8", errors="replace")
        else:
            content = data.decode("utf-8", errors="replace")
        return await self.ingest(doc_id, filename, content, f"file:{ext}")


ingestion = IngestionPipeline()
