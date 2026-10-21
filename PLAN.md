# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

document-deletion

## Roadmap

### baseline-completion — Complete Product Baseline

Status: done

Acceptance:
- Backend restructured to backend/app/main.py with proper module layout
- All required files present: portfolio.json, CHANGELOG.md, pyproject.toml, compose.yaml, package-lock.json, .github/workflows/ci.yml
- At least 12 meaningful backend pytest tests passing
- At least 3 meaningful frontend vitest tests passing
- Source code within 50-150KB budget
- Docker builds and healthchecks pass

Implementation: `backend/app/main.py`, `backend/app/routes.py`, `backend/app/retrieval.py`, `backend/app/vector_store.py`, `backend/app/chunking.py`, `backend/app/ingestion.py`, `backend/app/llm.py`, `backend/app/auth.py`, `backend/app/middleware.py`, `backend/app/config.py`, `backend/app/utils.py`, `frontend/src/App.tsx`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/Documents.tsx`, `frontend/src/pages/Query.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/pages/DocumentDetail.tsx`, `frontend/src/components/Sidebar.tsx`, `portfolio.json`, `CHANGELOG.md`, `pyproject.toml`, `compose.yaml`, `frontend/package-lock.json`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_auth.py`, `backend/tests/test_chunking.py`, `backend/tests/test_config.py`, `backend/tests/test_ingestion.py`, `backend/tests/test_integration.py`, `backend/tests/test_llm.py`, `backend/tests/test_middleware.py`, `backend/tests/test_retrieval.py`, `backend/tests/test_routes.py`, `backend/tests/test_utils.py`, `backend/tests/test_vector_store.py`, `frontend/src/components/__tests__/Sidebar.test.tsx`, `frontend/src/pages/__tests__/Dashboard.test.tsx`, `frontend/src/pages/__tests__/Documents.test.tsx`, `frontend/src/pages/__tests__/Query.test.tsx`

### persistent-vector-store — Persistent Vector Store with SQLite

Status: done

Acceptance:
- Vector store persists embeddings to SQLite database
- Survives container restarts
- Migration from in-memory store works
- Search performance acceptable for 10k+ vectors

Implementation: `backend/app/vector_store.py`, `backend/app/config.py`, `backend/app/routes.py`, `backend/requirements.txt`, `pyproject.toml`, `.env.example`

Tests: `backend/tests/test_vector_store.py`, `backend/tests/test_integration.py`, `backend/tests/test_routes.py`, `backend/tests/conftest.py`

### file-upload-ingestion — File Upload Document Ingestion

Status: done

Acceptance:
- POST /api/documents/upload accepts multipart file upload
- Supports PDF, DOCX, HTML, TXT, MD extraction
- Returns document ID and chunk count

Implementation: `backend/app/routes.py`, `backend/app/ingestion.py`, `frontend/src/pages/Documents.tsx`

Tests: `backend/tests/test_routes.py`, `backend/tests/test_ingestion.py`, `frontend/src/pages/__tests__/Documents.test.tsx`

### oidc-keycloak-auth — OIDC/Keycloak Authentication

Status: done

Acceptance:
- Authorization code flow with PKCE
- Keycloak realm import provided
- Session management with HttpOnly cookies
- CSRF protection on writes
- Role-based access (viewer/operator/admin)

Implementation: `backend/app/auth.py`, `backend/app/config.py`, `backend/app/routes.py`, `backend/app/middleware.py`, `backend/app/main.py`, `keycloak/realm-import.json`, `frontend/src/pages/Login.tsx`, `frontend/src/pages/Settings.tsx`, `frontend/src/components/Sidebar.tsx`, `frontend/src/App.tsx`

Tests: `backend/tests/test_auth.py`, `backend/tests/test_routes.py`, `frontend/src/components/__tests__/Sidebar.test.tsx`

### document-extraction — Proper Document Text Extraction (PDF, DOCX, HTML)

Status: done

Acceptance:
- PDF text extraction using pypdf with graceful fallback
- DOCX text extraction including paragraphs and tables using python-docx
- HTML text extraction using BeautifulSoup with script/style removal
- Plain text and markdown files continue to work as before
- Extraction failures logged but don't block ingestion

Implementation: `backend/app/ingestion.py`, `backend/requirements.txt`

Tests: `backend/tests/test_ingestion.py`

### document-deletion — Document Deletion API and UI

Status: done

Acceptance:
- DELETE /api/documents/{doc_id} endpoint removes document and all chunks
- Requires operator role for deletion
- CSRF protection on delete endpoint
- Frontend delete button on Document Detail page with confirmation
- Returns count of deleted chunks
- Document disappears from list after deletion

Implementation: `backend/app/routes.py`, `frontend/src/pages/DocumentDetail.tsx`

Tests: `backend/tests/test_routes.py`, `frontend/src/pages/__tests__/Documents.test.tsx`

