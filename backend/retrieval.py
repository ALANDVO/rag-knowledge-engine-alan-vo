"""RAG retrieval and generation pipeline."""
import structlog
from llm import chat, embed
from chunking import chunk_text
from vector_store import store
from config import get_settings

log = structlog.get_logger()


class RAGPipeline:
    async def index_document(self, doc_id: str, text: str, metadata: dict = None):
        s = get_settings()
        chunks = chunk_text(text, s.chunk_size, s.chunk_overlap)
        log.info("index_start", doc_id=doc_id, chunks=len(chunks))
        for i, chunk in enumerate(chunks):
            embeddings = await embed([chunk])
            await store.add(f"{doc_id}_{i}", chunk, embeddings[0], doc_id,
                            {"chunk_index": i, **(metadata or {})})
        log.info("index_done", doc_id=doc_id, chunks=len(chunks))
        return len(chunks)

    async def query(self, question: str, top_k: int = None) -> dict:
        s = get_settings()
        k = top_k or s.top_k
        log.info("rag_query", question=question[:100])
        query_emb = (await embed([question]))[0]
        context_docs = await store.search(query_emb, k)
        context = "\n\n".join(d["text"] for d in context_docs)
        prompt = (
            "You are a knowledgeable assistant. Use the provided context to answer the question.
"
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )
        answer = await chat([{"role": "user", "content": prompt}], temperature=0.3)
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {"doc_id": d["doc_id"], "score": round(d["score"], 4),
                 "text_preview": d["text"][:200]}
                for d in context_docs
            ],
            "context_chunks": len(context_docs),
        }


rag = RAGPipeline()
