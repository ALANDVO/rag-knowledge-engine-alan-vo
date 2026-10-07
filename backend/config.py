"""Application configuration."""
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    host: str = "0.0.0.0"
    port: int = 8000
    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    require_sso: bool = True
    llm_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1024")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "128")),
            top_k=int(os.getenv("TOP_K", "5")),
            require_sso=os.getenv("REQUIRE_SSO", "true") == "true",
            llm_model=os.getenv("LLM_MODEL", "gpt-4"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        )
    return _settings
