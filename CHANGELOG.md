# Changelog

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — 2026-10-21

### Added
- **Document Deletion** API and UI
  - DELETE /api/documents/{doc_id} endpoint removes document and all chunks
  - Requires operator role for deletion
  - CSRF protection on delete endpoint
  - Frontend delete button on Document Detail page with confirmation dialog
  - Returns count of deleted chunks
  - Document disappears from list after deletion
- New backend tests for delete endpoint (success, not found)

## 1.1.0 — work-in-progress checkpoint
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-13

### Added
- **Proper Document Text Extraction** for PDF, DOCX, and HTML files
  - PDF text extraction using `pypdf` with graceful fallback to raw content
  - DOCX text extraction including paragraphs and tables using `python-docx`
  - HTML text extraction using `BeautifulSoup` with script/style removal
  - Plain text and markdown files continue to work as before
  - Extraction failures logged but don't block ingestion
- New dependencies: `pypdf>=5.0.0`, `python-docx>=1.1.0`, `beautifulsoup4>=4.12.0`, `lxml>=5.2.0`

### Fixed
- Removed `backend/.venv` from git tracking (was incorrectly staged)
- Removed duplicate `.js` files in frontend (kept only `.tsx` TypeScript files)
- Cleaned up CHANGELOG duplicate entries

## [1.1.0] - 2026-10-13

### Added
- **OIDC/Keycloak Authentication** with authorization code flow and PKCE
- Session management with HttpOnly, SameSite=Lax cookies
- CSRF protection using double-submit pattern for state-changing operations
- Role-based access control (viewer, operator, admin)
- Keycloak realm import configuration (`keycloak/realm-import.json`)
- Login page (`/login`) with OIDC redirect
- User info display in sidebar with logout functionality
- `/api/auth/me`, `/api/auth/login`, `/api/auth/callback`, `/api/auth/logout`, `/api/auth/csrf` endpoints
- Protected routes requiring authentication
- Demo mode (`DEMO_MODE=true`) for development without Keycloak

### Changed
- Authentication now uses session cookies instead of Bearer tokens
- `get_current_user` dependency returns `User` object with role checking methods
- Added `require_sso` config option to toggle SSO requirement
- Added `SESSION_SECRET` for cookie signing
- Updated all protected API endpoints to validate CSRF tokens on mutations
- Frontend `App.tsx` now provides `AuthContext` with `useAuth` hook
- Sidebar displays authenticated user name, roles, and logout button
- Settings page shows current user info and uses CSRF token for saves
- Added `SessionInitMiddleware` to initialize auth managers

### Fixed
- Updated test suite to work with new session-based authentication
- Fixed middleware test to expect 3 middlewares (SessionInit, RequestLogger, Error)
- Fixed auth tests for new User object and session cookie behavior

### Added
- **Persistent SQLite-backed vector store** replacing in-memory store
- Vector store survives container restarts with configurable `VECTOR_DB_PATH`
- New `VECTOR_DB_PATH` environment variable for database location
- `aiosqlite` dependency for async SQLite operations
- Vector store migration from in-memory to persistent storage
- Document deletion support (`delete_document` method)
- Async `count` property and `get_doc_ids()`, `get_document_chunks()` methods

### Changed
- Vector store now persists embeddings to SQLite database
- Updated config with `vector_db_path` setting
- Updated API routes to use new async vector store methods
- Updated tests to use temporary databases for isolation
- README updated with persistent store architecture
- Tech stack updated to include aiosqlite

### Fixed
- Frontend TypeScript build: added vitest globals and @testing-library/jest-dom types
- Frontend test setup: replaced `global` with `globalThis` for browser compatibility
- Added .dockerignore files for backend and frontend to exclude .venv, node_modules, and other build artifacts
- Updated portfolio.json with accurate summary and removed work-in-progress status
- Updated README header to include author name and AI/ML focus

### Added
- vitest configuration in vite.config.ts with jsdom environment and setup files
- @types/node dev dependency for frontend type support
- vitest.d.ts declaration file for jest-dom matchers

## [1.0.0] - 2026-10-13

### Added
- Initial RAG Knowledge Engine implementation
- FastAPI backend with document ingestion, vector search, and RAG pipeline
- React/TypeScript frontend with Dashboard, Documents, Query, Settings, and Document Detail pages
- In-memory vector store with cosine similarity search
- Semantic and fixed-size text chunking with configurable overlap
- Multi-provider LLM client (OpenAI-compatible, Anthropic, Gemini, Ollama) with mock fallback
- File upload document ingestion (PDF, DOCX, HTML, TXT, MD)
- Document listing and detail views
- Export endpoint for knowledge base backup
- Bearer token authentication (SSO-ready with OIDC/Keycloak preparation)
- Structured JSON logging with structlog
- Docker and docker-compose deployment configuration
- Health check endpoint
- Comprehensive test suite (125 backend tests, 24 frontend tests)
- CI/CD pipeline with GitHub Actions

### Changed
- Restructured backend to `backend/app/` package layout
- Updated Dockerfiles to use new module structure
- Enhanced Settings page with LLM provider configuration

### Fixed
- String formatting in RAG pipeline prompt template
- Chunking overlap validation
- Cosine similarity floating-point precision handling