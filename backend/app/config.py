"""Application configuration."""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    host: str = "0.0.0.0"
    port: int = 8000
    chunk_size: int = 1024
    chunk_overlap: int = 128
    top_k: int = 5
    require_sso: bool = True
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    llm_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    vector_db_path: str = "data/vectors.db"
    # OIDC/Keycloak settings
    oidc_issuer_url: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_redirect_uri: Optional[str] = None
    session_secret: str = "dev-secret-change-in-production"
    demo_mode: bool = False


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
            require_sso=os.getenv("REQUIRE_SSO", "true").lower() == "true",
            llm_model=os.getenv("LLM_MODEL", "gpt-4"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "data/vectors.db"),
            oidc_issuer_url=os.getenv("OIDC_ISSUER_URL"),
            oidc_client_id=os.getenv("OIDC_CLIENT_ID"),
            oidc_client_secret=os.getenv("OIDC_CLIENT_SECRET"),
            oidc_redirect_uri=os.getenv("OIDC_REDIRECT_URI"),
            session_secret=os.getenv("SESSION_SECRET", "dev-secret-change-in-production"),
            demo_mode=os.getenv("DEMO_MODE", "false").lower() == "true",
        )
    return _settings