"""Tests for vector store functionality."""
import pytest
from app.vector_store import VectorStore, VectorRecord, cosine_similarity


class TestCosineSimilarity:
    """Tests for cosine similarity calculation."""

    def test_identical_vectors_returns_one(self):
        a = [1.0, 2.0, 3.0]
        assert cosine_similarity(a, a) == 1.0

    def test_orthogonal_vectors_returns_zero(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == 0.0

    def test_opposite_vectors_returns_negative_one(self):
        a = [1.0, 2.0]
        b = [-1.0, -2.0]
        result = cosine_similarity(a, b)
        assert abs(result - (-1.0)) < 1e-10

    def test_zero_vector_returns_zero(self):
        a = [0.0, 0.0, 0.0]
        b = [1.0, 2.0, 3.0]
        assert cosine_similarity(a, b) == 0.0

    def test_different_dimensions_handled(self):
        a = [1.0, 2.0, 3.0]
        b = [1.0, 2.0]
        # zip truncates to shorter, norms use full vectors
        result = cosine_similarity(a, b)
        expected = 5.0 / (14**0.5 * 5**0.5)  # dot=5, norm_a=sqrt(14), norm_b=sqrt(5)
        assert abs(result - expected) < 1e-10


class TestVectorStore:
    """Tests for VectorStore class."""

    @pytest.fixture
    def store(self, tmp_path):
        db_path = tmp_path / "test_vectors.db"
        return VectorStore(str(db_path))

    @pytest.mark.asyncio
    async def test_add_and_count(self, store):
        await store.add("id1", "text1", [1.0, 0.0], "doc1", {})
        assert await store.count == 1
        await store.add("id2", "text2", [0.0, 1.0], "doc1", {})
        assert await store.count == 2

    @pytest.mark.asyncio
    async def test_search_empty_store_returns_empty(self, store):
        results = await store.search([1.0, 0.0], top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_search_returns_most_similar_first(self, store):
        await store.add("id1", "text1", [1.0, 0.0], "doc1", {})
        await store.add("id2", "text2", [0.0, 1.0], "doc2", {})
        await store.add("id3", "text3", [0.9, 0.1], "doc3", {})
        results = await store.search([1.0, 0.0], top_k=3)
        assert len(results) == 3
        assert results[0]["id"] == "id1"
        assert results[1]["id"] == "id3"
        assert results[2]["id"] == "id2"

    @pytest.mark.asyncio
    async def test_search_respects_top_k(self, store):
        for i in range(10):
            await store.add(f"id{i}", f"text{i}", [float(i)/10, 0.0], f"doc{i}", {})
        results = await store.search([1.0, 0.0], top_k=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_returns_metadata(self, store):
        await store.add("id1", "text1", [1.0, 0.0], "doc1", {"source": "test", "page": 5})
        results = await store.search([1.0, 0.0], top_k=1)
        assert results[0]["metadata"]["source"] == "test"
        assert results[0]["metadata"]["page"] == 5

    @pytest.mark.asyncio
    async def test_search_returns_score_and_text(self, store):
        await store.add("id1", "original text", [1.0, 0.0], "doc1", {})
        results = await store.search([1.0, 0.0], top_k=1)
        assert results[0]["score"] == 1.0
        assert results[0]["text"] == "original text"
        assert results[0]["doc_id"] == "doc1"

    @pytest.mark.asyncio
    async def test_multiple_docs_tracked_separately(self, store):
        await store.add("id1", "text1", [1.0, 0.0], "doc1", {})
        await store.add("id2", "text2", [1.0, 0.0], "doc2", {})
        doc_ids = await store.get_doc_ids()
        assert doc_ids == {"doc1", "doc2"}

class TestVectorRecord:
    """Tests for VectorRecord dataclass."""

    def test_creation_with_metadata(self):
        rec = VectorRecord("id1", "text", [1.0, 2.0], "doc1", {"key": "value"})
        assert rec.id == "id1"
        assert rec.text == "text"
        assert rec.embedding == [1.0, 2.0]
        assert rec.doc_id == "doc1"
        assert rec.metadata == {"key": "value"}

    def test_default_empty_metadata(self):
        rec = VectorRecord("id1", "text", [1.0], "doc1")
        assert rec.metadata == {}