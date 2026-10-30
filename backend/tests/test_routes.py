"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch


class TestAuth:
    """Tests for authentication."""

    def test_missing_authorization_header_returns_401(self, client):
        response = client.post("/api/documents", json={"title": "Test", "content": "Content"})
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_empty_bearer_token_accepted_when_sso_disabled(self, client):
        """With require_sso=False, empty bearer token is accepted."""
        response = client.post("/api/documents", headers={"Authorization": "Bearer "}, json={"title": "Test", "content": "Content"})
        assert response.status_code == 200

    def test_invalid_token_format_returns_401(self, client):
        response = client.post("/api/documents", headers={"Authorization": "Basic dXNlcjpwYXNz"}, json={"title": "Test", "content": "Content"})
        assert response.status_code == 401

    def test_valid_placeholder_token_works(self, client, auth_headers):
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = 1
            response = client.post("/api/documents", headers=auth_headers, json={"title": "Test", "content": "Content"})
            assert response.status_code == 200

class TestDocumentsEndpoint:
    """Tests for /api/documents endpoint."""

    def test_ingest_document_requires_title(self, client, auth_headers):
        response = client.post("/api/documents", headers=auth_headers, json={"content": "Content only"})
        assert response.status_code == 422

    def test_ingest_document_requires_content(self, client, auth_headers):
        response = client.post("/api/documents", headers=auth_headers, json={"title": "Title only"})
        assert response.status_code == 422

    def test_ingest_document_empty_title_rejected(self, client, auth_headers):
        response = client.post("/api/documents", headers=auth_headers, json={"title": "", "content": "Content"})
        assert response.status_code == 422

    def test_ingest_document_empty_content_rejected(self, client, auth_headers):
        response = client.post("/api/documents", headers=auth_headers, json={"title": "Title", "content": ""})
        assert response.status_code == 422

    def test_ingest_document_title_max_length(self, client, auth_headers):
        long_title = "A" * 501
        response = client.post("/api/documents", headers=auth_headers, json={"title": long_title, "content": "Content"})
        assert response.status_code == 422

    def test_ingest_document_success(self, client, auth_headers):
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = 3
            response = client.post("/api/documents", headers=auth_headers, json={"title": "Test Doc", "content": "Document content here"})
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "indexed"
            assert data["chunks"] == 3
            assert data["doc_id"].startswith("doc_")

    def test_ingest_document_metadata_optional(self, client, auth_headers):
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = 1
            response = client.post("/api/documents", headers=auth_headers, json={"title": "Test", "content": "Content", "metadata": {"source": "web"}})
            assert response.status_code == 200

    def test_upload_document_requires_file(self, client, auth_headers):
        response = client.post("/api/documents/upload", headers=auth_headers, data={})
        assert response.status_code == 422

    def test_upload_document_success(self, client, auth_headers):
        with patch("app.routes.ingestion.ingest_file", new_callable=AsyncMock) as mock_ingest, \
             patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index:
            from app.ingestion import Document
            mock_ingest.return_value = Document(doc_id="doc_1", title="test.txt", content="File content", source="file:txt", metadata={})
            mock_index.return_value = 2
            response = client.post("/api/documents/upload", headers=auth_headers, files={"file": ("test.txt", b"File content", "text/plain")})
            assert response.status_code == 200
            data = response.json()
            assert data["doc_id"] == "doc_1"
            assert data["title"] == "test.txt"
            assert data["source"] == "file:txt"
            assert data["chunks"] == 2
            assert data["status"] == "indexed"

    def test_upload_document_empty_file_rejected(self, client, auth_headers):
        response = client.post("/api/documents/upload", headers=auth_headers, files={"file": ("empty.txt", b"", "text/plain")})
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]

    def test_list_documents(self, client, auth_headers):
        from app.vector_store import store
        import asyncio
        # Get initial doc IDs
        initial_doc_ids = asyncio.run(store.get_doc_ids())
        try:
            asyncio.run(store.add("doc1_0", "text1", [1.0, 0.0], "doc1", {}))
            asyncio.run(store.add("doc2_0", "text2", [0.0, 1.0], "doc2", {}))
            response = client.get("/api/documents", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2 + len(initial_doc_ids)
            assert set(data["documents"]) == {"doc1", "doc2"} | initial_doc_ids
        finally:
            # Clean up test records
            asyncio.run(store.delete_document("doc2"))

    def test_delete_document_success(self, client, auth_headers):
        from app.vector_store import store
        import asyncio
        # Add a document first
        asyncio.run(store.add("doc1_0", "text1", [1.0, 0.0], "doc1", {}))
        asyncio.run(store.add("doc1_1", "text2", [0.0, 1.0], "doc1", {}))
        try:
            response = client.delete("/api/documents/doc1", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["doc_id"] == "doc1"
            assert data["deleted_chunks"] == 2
            assert data["status"] == "deleted"
            # Verify it's gone
            doc_ids = asyncio.run(store.get_doc_ids())
            assert "doc1" not in doc_ids
        finally:
            asyncio.run(store.delete_document("doc1"))

    def test_delete_document_not_found(self, client, auth_headers):
        response = client.delete("/api/documents/nonexistent", headers=auth_headers)
        # Should return 200 with deleted_chunks=0
        assert response.status_code == 200
        data = response.json()
        assert data["doc_id"] == "nonexistent"

    def test_delete_document_requires_operator_role(self, client, viewer_headers):
        from app.vector_store import store
        import asyncio
        # Add a document first (using operator)
        asyncio.run(store.add("doc1_0", "text1", [1.0, 0.0], "doc1", {}))
        try:
            # Try to delete with viewer role - should fail
            response = client.delete("/api/documents/doc1", headers=viewer_headers)
            assert response.status_code == 403
            assert "operator" in response.json()["detail"].lower()
        finally:
            asyncio.run(store.delete_document("doc1"))



class TestQueryEndpoint:

    def test_query_requires_question(self, client, auth_headers):
        response = client.post("/api/query", headers=auth_headers, json={})
        assert response.status_code == 422

    def test_query_question_min_length(self, client, auth_headers):
        response = client.post("/api/query", headers=auth_headers, json={"question": "?"})
        assert response.status_code == 422

    def test_query_question_max_length(self, client, auth_headers):
        long_q = "?" * 2001
        response = client.post("/api/query", headers=auth_headers, json={"question": long_q})
        assert response.status_code == 422

    def test_query_top_k_bounds(self, client, auth_headers):
        with patch("app.routes.rag.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = {"question": "Q", "answer": "A", "sources": [], "context_chunks": 0}
            response = client.post("/api/query", headers=auth_headers, json={"question": "Valid question?", "top_k": 0})
            assert response.status_code == 422
            response = client.post("/api/query", headers=auth_headers, json={"question": "Valid question?", "top_k": 21})
            assert response.status_code == 422

    def test_query_success(self, client, auth_headers):
        with patch("app.routes.rag.query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = {
                "question": "What is RAG?",
                "answer": "RAG stands for Retrieval-Augmented Generation.",
                "sources": [{"doc_id": "doc1", "score": 0.9, "text_preview": "RAG is..."}],
                "context_chunks": 1
            }
            response = client.post("/api/query", headers=auth_headers, json={"question": "What is RAG?"})
            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "What is RAG?"
            assert "RAG stands for" in data["answer"]
            assert len(data["sources"]) == 1


class TestStatsEndpoint:
    """Tests for /api/stats endpoint."""

    def test_stats_returns_vector_count(self, client, auth_headers):
        from app.vector_store import store
        import asyncio
        # Get initial count
        initial_count = asyncio.run(store.count)
        try:
            # Add some records to increase count
            asyncio.run(store.add("test1", "text", [1.0, 0.0], "doc1", {}))
            asyncio.run(store.add("test2", "text", [0.0, 1.0], "doc1", {}))
            response = client.get("/api/stats", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total_vectors"] == initial_count + 2
            assert data["status"] == "ok"
        finally:
            # Clean up test records
            asyncio.run(store.delete_document("doc1"))

class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


class TestCORS:
    """Tests for CORS headers."""

    def test_cors_headers_present(self, client):
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"