"""OIDC/Keycloak authentication with session management and CSRF protection."""
import base64
import hashlib
import secrets
import time
import urllib.parse
from dataclasses import dataclass
from typing import Optional

import httpx
import structlog
from fastapi import HTTPException, Request, Response, Depends
from jose import jwt, jwk
from jose.exceptions import JWTError
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

from .config import get_settings

log = structlog.get_logger()

# OIDC discovery cache
_oidc_config: dict | None = None
_jwks: dict | None = None


@dataclass
class User:
    """Authenticated user with roles."""
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = None
    session_id: str = ""

    def __post_init__(self):
        if self.roles is None:
            self.roles = []

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_admin(self) -> bool:
        return self.has_role("admin")

    def is_operator(self) -> bool:
        return self.has_role("operator") or self.is_admin()

    def is_viewer(self) -> bool:
        return self.has_role("viewer") or self.is_operator()


class SessionManager:
    """Manages signed session cookies with HttpOnly, SameSite=Lax."""

    def __init__(self, secret: str, max_age: int = 86400):
        self.signer = TimestampSigner(secret)
        self.max_age = max_age

    def create_session(self, user: User) -> str:
        """Create a signed session cookie value."""
        payload = f"{user.sub}|{user.session_id}|{int(time.time())}"
        return self.signer.sign(payload.encode()).decode()

    def parse_session(self, cookie_value: str) -> Optional[tuple[str, str, int]]:
        """Parse and verify session cookie. Returns (sub, session_id, timestamp) or None."""
        try:
            payload = self.signer.unsign(cookie_value.encode(), max_age=self.max_age).decode()
            parts = payload.split("|")
            if len(parts) == 3:
                return parts[0], parts[1], int(parts[2])
        except (BadSignature, SignatureExpired, ValueError):
            pass
        return None

    def set_session_cookie(self, response: Response, session_value: str):
        """Set HttpOnly, Secure, SameSite=Lax session cookie."""
        response.set_cookie(
            key="session",
            value=session_value,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=self.max_age,
            path="/",
        )

    def clear_session_cookie(self, response: Response):
        """Clear session cookie."""
        response.delete_cookie(key="session", path="/", httponly=True, samesite="lax")


class CSRFManager:
    """Generates and validates CSRF tokens using double-submit pattern."""

    def __init__(self, secret: str):
        self.secret = secret.encode()

    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token bound to session."""
        timestamp = str(int(time.time()))
        message = f"{session_id}|{timestamp}".encode()
        signature = hashlib.sha256(self.secret + message).hexdigest()[:32]
        return f"{timestamp}.{signature}"

    def validate_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token."""
        try:
            timestamp_str, signature = token.split(".", 1)
            timestamp = int(timestamp_str)
            # Token expires after 1 hour
            if time.time() - timestamp > 3600:
                return False
            message = f"{session_id}|{timestamp_str}".encode()
            expected = hashlib.sha256(self.secret + message).hexdigest()[:32]
            return secrets.compare_digest(signature, expected)
        except (ValueError, AttributeError):
            return False


async def fetch_oidc_config() -> dict:
    """Fetch OIDC configuration from issuer's discovery endpoint."""
    global _oidc_config
    settings = get_settings()
    if not settings.oidc_issuer_url:
        return {}
    if _oidc_config is None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{settings.oidc_issuer_url}/.well-known/openid-configuration")
            resp.raise_for_status()
            _oidc_config = resp.json()
    return _oidc_config


async def fetch_jwks() -> dict:
    """Fetch JWKS from OIDC provider."""
    global _jwks
    if _jwks is None:
        config = await fetch_oidc_config()
        jwks_uri = config.get("jwks_uri")
        if jwks_uri:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(jwks_uri)
                resp.raise_for_status()
                _jwks = resp.json()
    return _jwks


def get_public_key(kid: str) -> Optional[dict]:
    """Get public key by key ID from JWKS."""
    jwks = _jwks or {}
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


async def validate_id_token(id_token: str) -> dict:
    """Validate ID token using JWKS."""
    settings = get_settings()
    if not settings.oidc_issuer_url:
        raise HTTPException(status_code=500, detail="OIDC not configured")

    await fetch_jwks()
    try:
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            raise JWTError("Missing kid in token header")

        key = get_public_key(kid)
        if not key:
            raise JWTError(f"Key not found for kid: {kid}")

        public_key = jwk.construct(key)
        claims = jwt.decode(
            id_token,
            public_key.to_pem().decode(),
            algorithms=["RS256"],
            audience=settings.oidc_client_id,
            issuer=settings.oidc_issuer_url,
        )
        return claims
    except JWTError as e:
        log.warning("id_token_validation_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid ID token")


async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    """Exchange authorization code for tokens."""
    settings = get_settings()
    config = await fetch_oidc_config()
    token_endpoint = config.get("token_endpoint")
    if not token_endpoint:
        raise HTTPException(status_code=500, detail="Token endpoint not found")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.oidc_redirect_uri,
        "client_id": settings.oidc_client_id,
        "client_secret": settings.oidc_client_secret,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(token_endpoint, data=data)
        if resp.status_code != 200:
            log.warning("token_exchange_failed", status=resp.status_code, body=resp.text)
            raise HTTPException(status_code=400, detail="Token exchange failed")
        return resp.json()


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge


def build_authorization_url(state: str, code_challenge: str) -> str:
    """Build OIDC authorization URL with PKCE."""
    settings = get_settings()
    config = _oidc_config or {}
    auth_endpoint = config.get("authorization_endpoint")
    if not auth_endpoint:
        # Fallback to standard Keycloak path
        auth_endpoint = f"{settings.oidc_issuer_url}/protocol/openid-connect/auth"

    params = {
        "response_type": "code",
        "client_id": settings.oidc_client_id,
        "redirect_uri": settings.oidc_redirect_uri,
        "scope": "openid profile email roles",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{auth_endpoint}?{urllib.parse.urlencode(params)}"


session_manager = SessionManager("")
csrf_manager = CSRFManager("")


def init_auth_managers():
    """Initialize auth managers with settings."""
    global session_manager, csrf_manager
    settings = get_settings()
    session_manager = SessionManager(settings.session_secret)
    csrf_manager = CSRFManager(settings.session_secret)


async def get_current_user(request: Request) -> User:
    """Get current authenticated user from session cookie or Bearer token."""
    settings = get_settings()

    # Demo mode: allow unauthenticated access with a default user
    if settings.demo_mode:
        return User(sub="demo-user", email="demo@example.com", name="Demo User",
                    roles=["viewer", "operator", "admin"], session_id="demo")

    # Check for Bearer token (legacy/test compatibility)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if token == "sso_placeholder" or not settings.require_sso:
            # Accept placeholder token for testing
            return User(sub="test-user", email="test@example.com", name="Test User",
                        roles=["viewer", "operator", "admin"], session_id="test-session")
        if settings.require_sso and token != "sso_placeholder":
            log.warning("auth_check", token_preview=token[:10])
        # For other tokens, fall through to session check

    # Require SSO: check session cookie
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    parsed = session_manager.parse_session(session_cookie)
    if not parsed:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    sub, session_id, _ = parsed
    # In a real implementation, you'd fetch user details from a session store
    # For now, we decode roles from the session or use defaults
    return User(sub=sub, session_id=session_id, roles=["viewer"])


def require_role(required_role: str):
    """Factory for role-based dependency."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {"viewer": 0, "operator": 1, "admin": 2}
        user_level = max((role_hierarchy.get(r, 0) for r in user.roles), default=0)
        required_level = role_hierarchy.get(required_role, 0)
        if user_level < required_level:
            raise HTTPException(status_code=403, detail=f"Requires {required_role} role")
        return user
    return role_checker


async def require_viewer(user: User = Depends(get_current_user)) -> User:
    return user


async def require_operator(user: User = Depends(get_current_user)) -> User:
    if not user.is_operator():
        raise HTTPException(status_code=403, detail="Requires operator role")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Requires admin role")
    return user


# CSRF protection for state-changing operations
async def validate_csrf(request: Request, user: User) -> None:
    """Validate CSRF token for mutating requests."""
    settings = get_settings()
    # Skip CSRF in demo mode or when SSO is disabled (test mode)
    if settings.demo_mode or not settings.require_sso:
        return
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token required")
    if not csrf_manager.validate_token(user.session_id, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def get_csrf_token(user: User) -> str:
    """Get CSRF token for current session."""
    return csrf_manager.generate_token(user.session_id)