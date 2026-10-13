"""Persistent vector store with SQLite and cosine similarity."""
import math
import structlog
from dataclasses import dataclass, field
import json
import aiosqlite
from pathlib import Path

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
    """SQLite-backed persistent vector store with cosine similarity search."""

    def __init__(self, db_path: str = None):
        from .config import get_settings
        if db_path is None:
            db_path = get_settings().vector_db_path
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _init_db(self):
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_vectors_doc_id ON vectors(doc_id)
            """)
            await db.commit()
        self._initialized = True
        log.info("vector_store_initialized", db_path=str(self.db_path))

    async def add(self, rec_id: str, text: str, embedding: list[float],
                  doc_id: str, metadata: dict = None):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO vectors (id, text, embedding, doc_id, metadata) VALUES (?, ?, ?, ?, ?)",
                (rec_id, text, json.dumps(embedding), doc_id, json.dumps(metadata or {}))
            )
            await db.commit()
        log.debug("vector_added", id=rec_id, doc_id=doc_id)

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, text, embedding, doc_id, metadata FROM vectors"
            )
            rows = await cursor.fetchall()

        if not rows:
            return []

        scored = []
        for row in rows:
            rec_id, text, emb_json, doc_id, meta_json = row
            embedding = json.loads(emb_json)
            sim = cosine_similarity(query_embedding, embedding)
            metadata = json.loads(meta_json) if meta_json else {}
            scored.append((sim, {
                "id": rec_id,
                "text": text,
                "doc_id": doc_id,
                "metadata": metadata
            }))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [
            {"id": r["id"], "text": r["text"], "score": s, "doc_id": r["doc_id"],
             "metadata": r["metadata"]}
            for s, r in scored[:top_k]
        ]
        log.info("vector_search", query_dims=len(query_embedding), results=len(results))
        return results

    @property
    async def count(self) -> int:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM vectors")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_doc_ids(self) -> set[str]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT DISTINCT doc_id FROM vectors")
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

    async def get_document_chunks(self, doc_id: str) -> list[dict]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id, text, embedding, metadata FROM vectors WHERE doc_id = ? ORDER BY metadata",
                (doc_id,)
            )
            rows = await cursor.fetchall()
        results = []
        for row in rows:
            rec_id, text, emb_json, meta_json = row
            metadata = json.loads(meta_json) if meta_json else {}
            results.append({
                "id": rec_id,
                "text": text,
                "embedding": json.loads(emb_json),
                "metadata": metadata
            })
        return results

    async def delete_document(self, doc_id: str) -> int:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM vectors WHERE doc_id = ?", (doc_id,))
            await db.commit()
            deleted = cursor.rowcount
        log.info("document_deleted", doc_id=doc_id, chunks_deleted=deleted)
        return deleted


store = VectorStore()