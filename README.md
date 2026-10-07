# RAG Knowledge Engine

Enterprise-grade Retrieval-Augmented Generation platform with document ingestion, semantic chunking, vector search, and LLM-powered Q&A.

## Architecture

```
+------------------+       +-------------------+       +------------------+
|   React Frontend| <---> |   FastAPI Backend | <---> |    LLM Provider  |
|   (Vite + TS)   |  REST |   (Python 3.12)   |  API  |  (gpt-4, embed)  |
+------------------+       +-------------------+       +------------------+
                                  |
                         +------------------+
                         |  In-memory VStore |
                         |  (cosine sim)     |
                         +------------------+
```

## Features
- Document ingestion (PDF, DOCX, HTML, plain text)
- Semantic + fixed-size chunking with configurable overlap
- Cosine similarity vector search
- RAG pipeline: context retrieval -> LLM generation
- Bearer token auth (SSO-ready)
- Structured logging (structlog JSON)
- Docker + docker-compose deployment
- React/TypeScript dashboard with Documents, Query, Settings pages

## API Reference
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/documents | Ingest a document |
| POST | /api/query | Query the knowledge base |
| GET | /api/stats | Get vector store stats |
| GET | /health | Health check |

## Deployment

```bash
export LLM_API_KEY="your-key"
docker compose up -d
```

Frontend: http://localhost:3000
API: http://localhost:8000

## Tech Stack
- Backend: FastAPI, Python 3.12, structlog, Pydantic v2
- Frontend: React 18, TypeScript, Vite 6, React Router 7
- Infra: Docker, docker-compose, Nginx

---
Contact: alanvo@gmail.com
