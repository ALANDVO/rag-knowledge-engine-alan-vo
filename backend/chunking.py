"""Text chunking for RAG."""
import structlog
from config import get_settings

log = structlog.get_logger()


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[str]:
    s = get_settings()
    size = chunk_size or s.chunk_size
    overlap = chunk_overlap or s.chunk_overlap
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
    current = []
    current_len = 0
    max_size = get_settings().chunk_size
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > max_size and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks
