"""Tests for RAG retrieval pipeline."""
import pytest
from unittest.mock import AsyncMock, patch

from app.retrieval import RAGPipeline


class TestRAGPipeline:
    """Tests for RAGPipeline class."""

    @pytest.fixture
    def pipeline(self):
        return RAGPipeline()

    @pytest.mark.asyncio
    async def test_index_document_creates_chunks(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.add", new_callable=AsyncMock) as mock_add:
            mock_embed.return_value = [[0.1] * 64]
            text = "A" * 2500  # Will create multiple chunks with default 1024 size
            count = await pipeline.index_document("doc1", text, {"source": "test"})
            assert count > 1
            assert mock_embed.call_count == count
            assert mock_add.call_count == count

    @pytest.mark.asyncio
    async def test_index_document_empty_text(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.add", new_callable=AsyncMock) as mock_add:
            count = await pipeline.index_document("doc1", "", {})
            assert count == 0
            mock_embed.assert_not_called()
            mock_add.assert_not_called()

    @pytest.mark.asyncio
    async def test_index_document_whitespace_only(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.add", new_callable=AsyncMock) as mock_add:
            count = await pipeline.index_document("doc1", "   \n\t  ", {})
            assert count == 0
            mock_embed.assert_not_called()
            mock_add.assert_not_called()

    @pytest.mark.asyncio
    async def test_index_document_metadata_passed_through(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.add", new_callable=AsyncMock) as mock_add:
            mock_embed.return_value = [[0.1] * 64]
            await pipeline.index_document("doc1", "Hello world", {"author": "test", "page": 1})
            assert mock_add.call_count == 1
            call_args = mock_add.call_args
            # metadata is the 5th positional argument (index 4)
            metadata_arg = call_args.args[4]
            assert metadata_arg["author"] == "test"
            assert metadata_arg["page"] == 1
            assert metadata_arg["chunk_index"] == 0
    @pytest.mark.asyncio
    async def test_query_empty_store_returns_empty_sources(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.search", new_callable=AsyncMock) as mock_search, \
             patch("app.retrieval.chat", new_callable=AsyncMock) as mock_chat:
            mock_embed.return_value = [[0.1] * 64]
            mock_search.return_value = []
            mock_chat.return_value = "No relevant context found."
            result = await pipeline.query("What is this?", top_k=5)
            assert result["sources"] == []
            assert result["context_chunks"] == 0
            assert result["question"] == "What is this?"

    @pytest.mark.asyncio
    async def test_query_returns_sources_with_scores(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.search", new_callable=AsyncMock) as mock_search, \
             patch("app.retrieval.chat", new_callable=AsyncMock) as mock_chat:
            mock_embed.return_value = [[0.1] * 64]
            mock_search.return_value = [
                {"id": "doc1_0", "text": "Context text", "score": 0.95, "doc_id": "doc1", "metadata": {}},
                {"id": "doc1_1", "text": "More context", "score": 0.87, "doc_id": "doc1", "metadata": {}},
            ]
            mock_chat.return_value = "Based on context, the answer is X."
            result = await pipeline.query("Test question?", top_k=5)
            assert len(result["sources"]) == 2
            assert result["sources"][0]["doc_id"] == "doc1"
            assert result["sources"][0]["score"] == 0.95
            assert "Context text" in result["sources"][0]["text_preview"]
            assert result["context_chunks"] == 2

    @pytest.mark.asyncio
    async def test_query_top_k_limits_sources(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.search", new_callable=AsyncMock) as mock_search, \
             patch("app.retrieval.chat", new_callable=AsyncMock) as mock_chat:
            mock_embed.return_value = [[0.1] * 64]
            mock_search.return_value = [
                {"id": f"doc1_{i}", "text": f"Text {i}", "score": 0.9 - i*0.1, "doc_id": "doc1", "metadata": {}}
                for i in range(10)
            ]
            mock_chat.return_value = "Answer"
            result = await pipeline.query("Question?", top_k=3)
            # Verify store.search was called with top_k=3
            mock_search.assert_called_once()
            assert mock_search.call_args[0][1] == 3

    @pytest.mark.asyncio
    async def test_query_uses_default_top_k_when_none(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.search", new_callable=AsyncMock) as mock_search, \
             patch("app.retrieval.chat", new_callable=AsyncMock) as mock_chat, \
             patch("app.retrieval.get_settings") as mock_settings:
            mock_settings.return_value.top_k = 7
            mock_embed.return_value = [[0.1] * 64]
            mock_search.return_value = [{"id": "1", "text": "t", "score": 0.9, "doc_id": "d", "metadata": {}}] * 10
            mock_chat.return_value = "Answer"
            await pipeline.query("Q?", top_k=None)
            mock_search.assert_called_once()
            assert mock_search.call_args[0][1] == 7

    @pytest.mark.asyncio
    async def test_query_handles_llm_failure(self, pipeline):
        with patch("app.retrieval.embed", new_callable=AsyncMock) as mock_embed, \
             patch("app.retrieval.store.search", new_callable=AsyncMock) as mock_search, \
             patch("app.retrieval.chat", new_callable=AsyncMock) as mock_chat:
            mock_embed.return_value = [[0.1] * 64]
            mock_search.return_value = [{"id": "1", "text": "ctx", "score": 0.9, "doc_id": "d", "metadata": {}}]
            mock_chat.side_effect = Exception("LLM API error")
            with pytest.raises(Exception, match="LLM API error"):
                await pipeline.query("Q?")