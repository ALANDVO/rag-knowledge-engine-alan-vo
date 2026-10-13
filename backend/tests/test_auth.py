"""Tests for authentication."""
import pytest
from fastapi import HTTPException
from starlette.requests import Request
from unittest.mock import patch

from app.auth import get_current_user, User, SessionManager, CSRFManager


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def create_mock_request(self, auth_header: str = None, cookies: dict = None) -> Request:
        scope = {"type": "http", "headers": []}
        if auth_header:
            scope["headers"].append((b"authorization", auth_header.encode()))
        if cookies:
            cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
            scope["headers"].append((b"cookie", cookie_header.encode()))
        return Request(scope)

    @pytest.mark.asyncio
    async def test_missing_auth_raises(self):
        """Test that missing auth raises 401."""
        request = self.create_mock_request()
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            with pytest.raises(HTTPException) as exc:
                await get_current_user(request)
            assert exc.value.status_code == 401
            assert "Not authenticated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_non_bearer_scheme_raises(self):
        request = self.create_mock_request("Basic dXNlcjpwYXNz")
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            with pytest.raises(HTTPException) as exc:
                await get_current_user(request)
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_bearer_token_raises(self):
        request = self.create_mock_request("Bearer ")
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            with pytest.raises(HTTPException) as exc:
                await get_current_user(request)
            assert exc.value.status_code == 401
            assert "Not authenticated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_valid_placeholder_token_returns_user(self):
        request = self.create_mock_request("Bearer sso_placeholder")
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            user = await get_current_user(request)
        assert isinstance(user, User)
        assert user.sub == "test-user"
        assert "viewer" in user.roles
        assert "operator" in user.roles
        assert "admin" in user.roles

    @pytest.mark.asyncio
    async def test_invalid_token_with_sso_required_falls_to_session(self, caplog):
        """Invalid token falls through to session check which fails."""
        request = self.create_mock_request("Bearer invalid_token")
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            with pytest.raises(HTTPException) as exc:
                await get_current_user(request)
            assert exc.value.status_code == 401
            assert "Not authenticated" in exc.value.detail

    @pytest.mark.asyncio
    async def test_token_accepted_when_sso_not_required(self):
        request = self.create_mock_request("Bearer any_token")
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = False
            mock_settings.return_value.demo_mode = False
            user = await get_current_user(request)
        assert isinstance(user, User)
        assert user.sub == "test-user"

    @pytest.mark.asyncio
    async def test_session_cookie_authentication(self):
        """Test authentication via session cookie."""
        from app.auth import session_manager
        # Use global session_manager which is initialized with test settings
        session_value = session_manager.create_session(
            User(sub="cookie-user", session_id="session-123", roles=["viewer"])
        )
        request = self.create_mock_request(cookies={"session": session_value})
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            mock_settings.return_value.session_secret = "test-secret"
            user = await get_current_user(request)
        assert isinstance(user, User)
        assert user.sub == "cookie-user"
        assert user.session_id == "session-123"

    @pytest.mark.asyncio
    async def test_expired_session_cookie_rejected(self):
        """Test that expired session cookie is rejected."""
        from app.auth import SessionManager
        # Create a separate SessionManager with short max_age for this test
        test_session_manager = SessionManager("test-secret", max_age=1)
        session_value = test_session_manager.create_session(
            User(sub="cookie-user", session_id="session-123", roles=["viewer"])
        )
        import time
        time.sleep(1.1)
        request = self.create_mock_request(cookies={"session": session_value})
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.require_sso = True
            mock_settings.return_value.demo_mode = False
            mock_settings.return_value.session_secret = "test-secret"
            with pytest.raises(HTTPException) as exc:
                await get_current_user(request)
            assert exc.value.status_code == 401
            assert "Invalid or expired session" in exc.value.detail

    @pytest.mark.asyncio
    async def test_demo_mode_returns_default_user(self):
        request = self.create_mock_request()
        with patch("app.auth.get_settings") as mock_settings:
            mock_settings.return_value.demo_mode = True
            user = await get_current_user(request)
        assert isinstance(user, User)
        assert user.sub == "demo-user"
        assert "admin" in user.roles


class TestUserRoles:
    """Tests for User role checking."""

    def test_has_role(self):
        user = User(sub="test", roles=["viewer", "operator"])
        assert user.has_role("viewer")
        assert user.has_role("operator")
        assert not user.has_role("admin")

    def test_is_viewer(self):
        user = User(sub="test", roles=["viewer"])
        assert user.is_viewer()
        assert not user.is_operator()
        assert not user.is_admin()

    def test_is_operator(self):
        user = User(sub="test", roles=["operator"])
        assert user.is_viewer()
        assert user.is_operator()
        assert not user.is_admin()

    def test_is_admin(self):
        user = User(sub="test", roles=["admin"])
        assert user.is_viewer()
        assert user.is_operator()
        assert user.is_admin()


class TestSessionManager:
    """Tests for SessionManager."""

    def test_create_and_parse_session(self):
        manager = SessionManager("secret")
        user = User(sub="test-user", session_id="sess-123", roles=["viewer"])
        session_value = manager.create_session(user)
        parsed = manager.parse_session(session_value)
        assert parsed is not None
        assert parsed[0] == "test-user"
        assert parsed[1] == "sess-123"

    def test_invalid_signature_rejected(self):
        manager = SessionManager("secret")
        tampered = "invalid.signature"
        parsed = manager.parse_session(tampered)
        assert parsed is None


class TestCSRFManager:
    """Tests for CSRFManager."""

    def test_generate_and_validate_token(self):
        manager = CSRFManager("secret")
        token = manager.generate_token("session-123")
        assert manager.validate_token("session-123", token)
        assert not manager.validate_token("different-session", token)

    def test_expired_token_rejected(self):
        manager = CSRFManager("secret")
        # Manually create an old token
        import time
        old_timestamp = str(int(time.time()) - 3601)  # 1 hour + 1 second ago
        old_token = f"{old_timestamp}.{manager.generate_token('session-123').split('.')[1]}"
        assert not manager.validate_token("session-123", old_token)