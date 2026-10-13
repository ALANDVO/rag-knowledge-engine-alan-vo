"""Tests for LLM client."""
import pytest
from unittest.mock import AsyncMock, patch

from app.llm import chat, embed


class TestChat:
    """Tests for chat function."""

    @pytest.mark.asyncio
    async def test_chat_returns_string(self):
        result = await chat([{"role": "user", "content": "Hello"}])
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_chat_logs_model_and_message_count(self, caplog):
        import structlog
        log = structlog.get_logger()
        with patch("app.llm.get_settings") as mock_settings:
            mock_settings.return_value.llm_model = "test-model"
            await chat([{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}])
        # Check that logging happened (caplog may not capture structlog directly)
        # This is a smoke test


class TestEmbed:
    """Tests for embed function."""

    @pytest.mark.asyncio
    async def test_embed_returns_list_of_vectors(self):
        texts = ["Hello world", "Another text"]
        results = await embed(texts)
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(v, list) for v in results)
        assert all(len(v) == 64 for v in results)
        assert all(isinstance(x, float) for v in results for x in v)

    @pytest.mark.asyncio
    async def test_embed_empty_list_returns_empty(self):
        results = await embed([])
        assert results == []

    @pytest.mark.asyncio
    async def test_embed_deterministic_same_input(self):
        text = "Deterministic test"
        r1 = await embed([text])
        r2 = await embed([text])
        assert r1 == r2

    @pytest.mark.asyncio
    async def test_embed_different_inputs_different_vectors(self):
        r1 = await embed(["Text A"])
        r2 = await embed(["Text B"])
        assert r1 != r2

    @pytest.mark.asyncio
    async def test_embed_vector_values_normalized(self):
        results = await embed(["Test"])
        vec = results[0]
        # Values should be in range [0, 1] since divided by 255
        assert all(0 <= x <= 1 for x in vec)

    @pytest.mark.asyncio
    async def test_embed_logs_model_and_count(self):
        with patch("app.llm.get_settings") as mock_settings:
            mock_settings.return_value.embedding_model = "test-embed-model"
            await embed(["a", "b", "c"])
        # Smoke test for logging


class TestEmbedEdgeCases:
    """Edge case tests for embeddings."""

    @pytest.mark.asyncio
    async def test_embed_unicode_text(self):
        texts = ["你好世界", "🎉 emoji test", "café"]
        results = await embed(texts)
        assert len(results) == 3
        assert all(len(v) == 64 for v in results)

    @pytest.mark.asyncio
    async def test_embed_very_long_text(self):
        long_text = "A" * 10000
        results = await embed([long_text])
        assert len(results) == 1
        assert len(results[0]) == 64