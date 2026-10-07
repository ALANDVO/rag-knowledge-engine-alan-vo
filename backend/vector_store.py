"""In-memory vector store with cosine similarity."""
import math
import structlog
from dataclasses import dataclass, field

log = structlog.get_logger()


@dataclass
class VectorRecord:
    id: str
    text: str
    embedding: list[float]
    doc_id: str
    metadata: dict = field(default_factory=dict)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    def __init__(self):
        self.records: list[VectorRecord] = []

    async def add(self, rec_id: str, text: str, embedding: list[float],
                  doc_id: str, metadata: dict = None):
        self.records.append(VectorRecord(rec_id, text, embedding, doc_id, metadata or {}))
        log.debug("vector_added", id=rec_id, doc_id=doc_id, total=len(self.records))

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        if not self.records:
            return []
        scored = []
        for rec in self.records:
            sim = cosine_similarity(query_embedding, rec.embedding)
            scored.append((sim, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {"id": r.id, "text": r.text, "score": s, "doc_id": r.doc_id,
             "metadata": r.metadata}
            for s, r in scored[:top_k]
        ]
        log.info("vector_search", query_dims=len(query_embedding), results=len(results))
        return results

    @property
    def count(self) -> int:
        return len(self.records)


store = VectorStore()
