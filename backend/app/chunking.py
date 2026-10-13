"""Text chunking for RAG."""
import structlog
from .config import get_settings

log = structlog.get_logger()


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[str]:
    s = get_settings()
    size = chunk_size if chunk_size is not None else s.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else s.chunk_overlap
    if overlap >= size:
        raise ValueError("chunk_overlap must be less than chunk_size")
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        if end > len(text):
            end = len(text)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    log.info("chunking", total=len(text), chunks=len(chunks))
    return chunks


def chunk_semantic(text: str) -> list[str]:
    """Split on paragraph boundaries for semantic chunks."""
    paragraphs = text.split("\n\n")
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if para:
            chunks.append(para)
    return chunks
