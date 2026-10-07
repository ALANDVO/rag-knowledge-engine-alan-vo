"""RAG API routes."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel, Field
from retrieval import rag
from auth import get_current_user

log = structlog.get_logger()
router = APIRouter(prefix="/api", tags=["rag"])


class IngestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)


@router.post("/documents")
async def ingest_document(req: IngestRequest, user=Depends(get_current_user)):
    log.info("api_ingest", title=req.title, user=user.get("sub"))
    doc_id = f"doc_{len(rag._docs) + 1}"
    chunks = await rag.index_document(doc_id, req.content, req.metadata)
    return {"doc_id": doc_id, "chunks": chunks, "status": "indexed"}


@router.post("/query")
async def query(req: QueryRequest, user=Depends(get_current_user)):
    log.info("api_query", question=req.question[:80])
    return await rag.query(req.question, req.top_k)


@router.get("/stats")
async def stats(user=Depends(get_current_user)):
    from vector_store import store
    return {"total_vectors": store.count, "status": "ok"}
