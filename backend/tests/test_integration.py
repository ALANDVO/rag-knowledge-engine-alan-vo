"""Integration tests for API workflows."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


class TestFullWorkflow:
    """End-to-end workflow tests."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer sso_placeholder"}

    def test_ingest_then_query_workflow(self, client, auth_headers):
        """Test complete ingest -> query workflow."""
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index, \
             patch("app.routes.rag.query", new_callable=AsyncMock) as mock_query:
            mock_index.return_value = 2
            mock_query.return_value = {
                "question": "What is the capital of France?",
                "answer": "Paris is the capital of France.",
                "sources": [
                    {"doc_id": "doc_1", "score": 0.95, "text_preview": "France is a country in Europe. Its capital is Paris."}
                ],
                "context_chunks": 1
            }

            # Step 1: Ingest document
            ingest_resp = client.post(
                "/api/documents",
                headers=auth_headers,
                json={"title": "France Facts", "content": "France is a country in Europe. Its capital is Paris."}
            )
            assert ingest_resp.status_code == 200
            ingest_data = ingest_resp.json()
            assert ingest_data["status"] == "indexed"
            assert ingest_data["chunks"] == 2
            doc_id = ingest_data["doc_id"]

            # Step 2: Query
            query_resp = client.post(
                "/api/query",
                headers=auth_headers,
                json={"question": "What is the capital of France?"}
            )
            assert query_resp.status_code == 200
            query_data = query_resp.json()
            assert query_data["question"] == "What is the capital of France?"
            assert "Paris" in query_data["answer"]
            assert len(query_data["sources"]) == 1
            assert query_data["sources"][0]["doc_id"] == doc_id

    def test_multiple_documents_query_returns_all_relevant(self, client, auth_headers):
        """Test querying with multiple documents."""
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index, \
             patch("app.routes.rag.query", new_callable=AsyncMock) as mock_query:
            mock_index.return_value = 1
            mock_query.return_value = {
                "question": "Compare Python and JavaScript",
                "answer": "Python uses indentation; JavaScript uses braces.",
                "sources": [
                    {"doc_id": "doc_1", "score": 0.9, "text_preview": "Python uses significant whitespace..."},
                    {"doc_id": "doc_2", "score": 0.85, "text_preview": "JavaScript uses curly braces..."},
                ],
                "context_chunks": 2
            }

            client.post("/api/documents", headers=auth_headers, json={"title": "Python", "content": "Python uses significant whitespace for blocks."})
            client.post("/api/documents", headers=auth_headers, json={"title": "JavaScript", "content": "JavaScript uses curly braces for blocks."})
            query_resp = client.post("/api/query", headers=auth_headers, json={"question": "Compare Python and JavaScript"})
            assert query_resp.status_code == 200
            data = query_resp.json()
            assert len(data["sources"]) == 2
            doc_ids = {s["doc_id"] for s in data["sources"]}
            assert "doc_1" in doc_ids
            assert "doc_2" in doc_ids

    def test_stats_reflects_ingested_documents(self, client, auth_headers):
        """Test stats endpoint shows vector count."""
        from app.vector_store import store
        import asyncio
        # Get initial count
        initial_count = asyncio.run(store.count)
        try:
            for i in range(15):
                asyncio.run(store.add(f"test{i}", "text", [1.0, 0.0], f"doc{i}", {}))
            resp = client.get("/api/stats", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["total_vectors"] == initial_count + 15
        finally:
            # Clean up test records
            for i in range(15):
                asyncio.run(store.delete_document(f"doc{i}"))

class TestErrorHandling:
    """Tests for error handling in workflows."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        return {"Authorization": "Bearer sso_placeholder"}

    def test_ingest_failure_returns_500(self, client, auth_headers):
        with patch("app.routes.rag.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.side_effect = Exception("Vector store unavailable")
            resp = client.post("/api/documents", headers=auth_headers, json={"title": "Test", "content": "Content"})
            # ErrorMiddleware catches and returns 500
            assert resp.status_code == 500
            assert resp.json()["error"] == "Internal server error"

    def test_query_failure_returns_500(self, client, auth_headers):
        with patch("app.routes.rag.query", new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("LLM timeout")
            resp = client.post("/api/query", headers=auth_headers, json={"question": "Test?"})
            assert resp.status_code == 500
            assert resp.json()["error"] == "Internal server error"