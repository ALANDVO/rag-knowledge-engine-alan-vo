# RAG Knowledge Engine | Alan Vo | AI & Machine Learning

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


Enterprise-grade Retrieval-Augmented Generation platform with document ingestion, semantic chunking, persistent vector search, and LLM-powered Q&A.

## Architecture

```
+------------------+       +-------------------+       +------------------+
|   React Frontend| <---> |   FastAPI Backend | <---> |    LLM Provider  |
|   (Vite + TS)   |  REST |   (Python 3.12)   |  API  |  (OpenAI, etc.)  |
+------------------+       +-------------------+       +------------------+
                                  |
                         +------------------+
                         |  SQLite VStore   |
                         |  (cosine sim)    |
                         +------------------+
```

## Features

- Document ingestion (PDF, DOCX, HTML, plain text) via JSON or file upload with **proper text extraction**
- Semantic + fixed-size chunking with configurable overlap
- Cosine similarity vector search with **SQLite-persistent store**
- RAG pipeline: context retrieval -> LLM generation with source citations
- Multi-provider LLM client: OpenAI-compatible, Anthropic, Google Gemini, Ollama
- Document listing, detail view, and knowledge base export
- OIDC/Keycloak authentication with session cookies, PKCE, and CSRF protection
- Role-based access control (viewer, operator, admin)
- Structured JSON logging with structlog
- Docker + docker-compose deployment with persistent volumes
- React/TypeScript dashboard with Dashboard, Documents, Query, Settings, Document Detail pages
- Comprehensive test suite (136 backend, 25 frontend tests)
- CI/CD with GitHub Actions

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/documents | Ingest a document (JSON) |
| POST | /api/documents/upload | Upload and ingest a file |
| GET | /api/documents | List all documents |
| GET | /api/documents/{doc_id} | Get document details |
| POST | /api/query | Query the knowledge base |
| GET | /api/stats | Get vector store stats |
| GET | /api/export | Export knowledge base |
| GET | /health | Health check |
| GET | /api/auth/login | Initiate OIDC login |
| GET | /api/auth/callback | OIDC callback handler |
| POST | /api/auth/logout | Logout and clear session |
| GET | /api/auth/me | Get current user info |
| GET | /api/auth/csrf | Get CSRF token |

## Deployment

```bash
export LLM_API_KEY="your-key"
docker compose up -d
```

Frontend: http://localhost:3000
API: http://localhost:8000

## Tech Stack

- Backend: FastAPI, Python 3.12, structlog, Pydantic v2, httpx, aiosqlite, pypdf, python-docx, beautifulsoup4
- Frontend: React 18, TypeScript, Vite 6, React Router 7, Vitest
- Infra: Docker, docker-compose, Nginx, Keycloak

## LLM Provider Configuration

| Provider | Environment Variables |
|----------|----------------------|
| OpenAI / OpenRouter | LLM_API_KEY, LLM_BASE_URL, LLM_MODEL |
| Anthropic | LLM_API_KEY, LLM_BASE_URL, LLM_MODEL |
| Google Gemini | LLM_API_KEY, LLM_BASE_URL, LLM_MODEL |
| Ollama (Local) | LLM_BASE_URL, LLM_MODEL |

Default embedding model: `text-embedding-3-small`

## AI/ML Evaluation

The RAG pipeline uses deterministic hash-based embeddings for testing. With a real LLM API key:

```bash
# Ingest test documents
curl -X POST http://localhost:8000/api/documents \
  -H "Authorization: Bearer sso_placeholder" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Your document content"}'

# Query the knowledge base
curl -X POST http://localhost:8000/api/query \
  -H "Authorization: Bearer sso_placeholder" \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

**Vector store**: SQLite-backed persistent storage survives container restarts. Configure with `VECTOR_DB_PATH` environment variable.

**Document extraction**: PDF (pypdf), DOCX (python-docx), HTML (BeautifulSoup) text extraction with graceful fallback for corrupted files.

## Security

- OIDC/Keycloak authentication with authorization code flow + PKCE
- Session cookies: HttpOnly, SameSite=Lax, signed with SESSION_SECRET
- CSRF protection via double-submit pattern on all mutating endpoints
- Role-based access control (viewer, operator, admin)
- CORS configured for frontend origin
- Structured logging without sensitive data
- No secrets in code or logs
- API keys only server-side, never exposed to frontend

## Testing

```bash
# Backend tests
cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -v

# Frontend tests
cd frontend && npm test
```

---

Contact: alanvo@gmail.com