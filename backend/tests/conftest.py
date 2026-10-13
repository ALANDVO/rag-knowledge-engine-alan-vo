"""Test configuration and fixtures."""
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# Ensure backend is on path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings


# Test settings with SSO disabled for easier testing
TEST_SETTINGS = Settings(
    host="0.0.0.0",
    port=8000,
    chunk_size=1024,
    chunk_overlap=128,
    top_k=5,
    require_sso=False,  # Disable SSO requirement for tests
    llm_model="gpt-4",
    embedding_model="text-embedding-3-small",
    vector_db_path="data/vectors.db",
    oidc_issuer_url=None,
    oidc_client_id=None,
    oidc_client_secret=None,
    oidc_redirect_uri=None,
    session_secret="test-secret",
    demo_mode=False,
)


@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for all tests."""
    with patch("app.config.get_settings", return_value=TEST_SETTINGS):
        with patch("app.auth.get_settings", return_value=TEST_SETTINGS):
            yield


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authorization headers for testing."""
    return {"Authorization": "Bearer sso_placeholder"}


@pytest.fixture(autouse=True)
def reset_vector_store():
    """Reset vector store before each test using a temporary database."""
    from app.vector_store import store

    # Create a temporary database for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = tmp.name

    # Replace the store's database path
    original_db_path = store.db_path
    store.db_path = Path(test_db_path)
    store._initialized = False

    yield

    # Cleanup: remove temp database and restore original
    try:
        os.unlink(test_db_path)
    except OSError:
        pass
    store.db_path = original_db_path
    store._initialized = False