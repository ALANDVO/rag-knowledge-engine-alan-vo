"""Tests for configuration."""
import os
from unittest.mock import patch

from app.config import Settings, get_settings


class TestSettings:
    """Tests for Settings dataclass."""

    def test_default_values(self):
        s = Settings()
        assert s.host == "0.0.0.0"
        assert s.port == 8000
        assert s.chunk_size == 1024
        assert s.chunk_overlap == 128
        assert s.top_k == 5
        assert s.require_sso is True
        assert s.llm_model == "gpt-4"
        assert s.embedding_model == "text-embedding-3-small"

    def test_custom_values(self):
        s = Settings(host="127.0.0.1", port=9000, chunk_size=512, require_sso=False)
        assert s.host == "127.0.0.1"
        assert s.port == 9000
        assert s.chunk_size == 512
        assert s.require_sso is False


class TestGetSettings:
    """Tests for get_settings function."""

    def test_singleton_pattern(self):
        # Reset global
        import app.config
        app.config._settings = None
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_reads_from_environment(self):
        import app.config
        app.config._settings = None
        with patch.dict(os.environ, {
            "HOST": "1.2.3.4",
            "PORT": "9999",
            "CHUNK_SIZE": "2048",
            "CHUNK_OVERLAP": "256",
            "TOP_K": "10",
            "REQUIRE_SSO": "false",
            "LLM_MODEL": "gpt-3.5-turbo",
            "EMBEDDING_MODEL": "text-embedding-ada-002",
        }):
            s = get_settings()
            assert s.host == "1.2.3.4"
            assert s.port == 9999
            assert s.chunk_size == 2048
            assert s.chunk_overlap == 256
            assert s.top_k == 10
            assert s.require_sso is False
            assert s.llm_model == "gpt-3.5-turbo"
            assert s.embedding_model == "text-embedding-ada-002"

    def test_require_sso_case_insensitive(self):
        import app.config
        app.config._settings = None
        with patch.dict(os.environ, {"REQUIRE_SSO": "FALSE"}):
            s = get_settings()
            assert s.require_sso is False
        app.config._settings = None
        with patch.dict(os.environ, {"REQUIRE_SSO": "True"}):
            s = get_settings()
            assert s.require_sso is True