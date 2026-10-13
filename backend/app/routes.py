"""RAG API routes."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request, Response
from pydantic import BaseModel, Field
from .retrieval import rag
from .auth import (
    get_current_user,
    require_role,
    User,
    validate_csrf,
    get_csrf_token,
    build_authorization_url,
    generate_pkce_pair,
    exchange_code_for_tokens,
    validate_id_token,
    session_manager,
)
from .ingestion import ingestion
from .config import get_settings

log = structlog.get_logger()
router = APIRouter(prefix="/api", tags=["rag"])


class IngestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(5, ge=1, le=20)


class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    source: str
    chunks: int
    status: str


# ===== Authentication Endpoints =====

@router.get("/auth/login")
async def login(request: Request):
    """Initiate OIDC authorization code flow with PKCE."""
    settings = get_settings()
    if not settings.oidc_issuer_url or not settings.oidc_client_id:
        raise HTTPException(status_code=503, detail="OIDC not configured")

    # Generate PKCE pair and state
    code_verifier, code_challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(32)

    # Store PKCE verifier and state in session (using a temporary cookie)
    # In production, use a server-side session store
    pkce_cookie = f"{code_verifier}|{state}"
    signed_pkce = session_manager.signer.sign(pkce_cookie.encode()).decode()

    auth_url = build_authorization_url(state, code_challenge)

    response = Response(content="", status_code=302)
    response.headers["Location"] = auth_url
    response.set_cookie(
        key="pkce",
        value=signed_pkce,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=600,  # 10 minutes
        path="/",
    )
    return response


@router.get("/auth/callback")
async def callback(request: Request, response: Response, code: str = None, state: str = None, error: str = None):
    """Handle OIDC callback and exchange code for tokens."""
    settings = get_settings()

    if error:
        log.warning("oidc_callback_error", error=error)
        raise HTTPException(status_code=400, detail=f"Authentication failed: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    # Retrieve and verify PKCE verifier and state
    pkce_cookie = request.cookies.get("pkce")
    if not pkce_cookie:
        raise HTTPException(status_code=400, detail="Missing PKCE session")

    try:
        pkce_data = session_manager.signer.unsign(pkce_cookie.encode(), max_age=600).decode()
        stored_verifier, stored_state = pkce_data.split("|", 1)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid PKCE session")

    if not secrets.compare_digest(state, stored_state):
        raise HTTPException(status_code=400, detail="State mismatch")

    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(code, stored_verifier)
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="No ID token returned")

    # Validate ID token
    claims = await validate_id_token(id_token)

    # Extract user info and roles
    sub = claims.get("sub")
    email = claims.get("email")
    name = claims.get("name") or claims.get("preferred_username")
    # Keycloak realm roles are in "realm_access.roles"
    realm_roles = claims.get("realm_access", {}).get("roles", [])
    # Also check resource access for client roles
    client_roles = claims.get("resource_access", {}).get(settings.oidc_client_id, {}).get("roles", [])
    all_roles = list(set(realm_roles + client_roles))

    # Map Keycloak roles to our roles
    role_mapping = {
        "admin": "admin",
        "operator": "operator",
        "viewer": "viewer",
        "rag-admin": "admin",
        "rag-operator": "operator",
        "rag-viewer": "viewer",
    }
    mapped_roles = []
    for role in all_roles:
        if role in role_mapping:
            mapped_roles.append(role_mapping[role])
    if not mapped_roles:
        mapped_roles = ["viewer"]

    # Create user and session
    session_id = secrets.token_urlsafe(16)
    user = User(
        sub=sub,
        email=email,
        name=name,
        roles=mapped_roles,
        session_id=session_id,
    )

    session_value = session_manager.create_session(user)
    session_manager.set_session_cookie(response, session_value)

    # Clear PKCE cookie
    response.delete_cookie(key="pkce", path="/", httponly=True, samesite="lax")

    # Redirect to frontend
    frontend_url = settings.oidc_redirect_uri.replace("/api/auth/callback", "") if settings.oidc_redirect_uri else "/"
    response.headers["Location"] = frontend_url
    response.status_code = 302
    return response


@router.post("/auth/logout")
async def logout(request: Request, response: Response, user: User = Depends(get_current_user)):
    """Logout and clear session."""
    session_manager.clear_session_cookie(response)
    return {"status": "logged_out"}


@router.get("/auth/me")
async def me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "sub": user.sub,
        "email": user.email,
        "name": user.name,
        "roles": user.roles,
    }


@router.get("/auth/csrf")
async def csrf_token(user: User = Depends(get_current_user)):
    """Get CSRF token for current session."""
    token = get_csrf_token(user)
    return {"csrf_token": token}


# ===== RAG Endpoints (protected) =====

@router.post("/documents")
async def ingest_document(
    req: IngestRequest,
    request: Request,
    user: User = Depends(get_current_user),
):
    await validate_csrf(request, user)
    log.info("api_ingest", title=req.title, user=user.sub)
    doc_id = f"doc_{len(rag._docs) + 1}"
    chunks = await rag.index_document(doc_id, req.content, req.metadata)
    return {"doc_id": doc_id, "chunks": chunks, "status": "indexed"}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Query(None, min_length=1, max_length=500),
    request: Request = None,
    user: User = Depends(get_current_user),
):
    await validate_csrf(request, user)
    log.info("api_upload", filename=file.filename, user=user.sub)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    doc_title = title or file.filename or "Untitled"
    doc = await ingestion.ingest_file(f"doc_{len(rag._docs) + 1}", doc_title, data)
    chunks = await rag.index_document(doc.doc_id, doc.content, doc.metadata)
    return DocumentResponse(
        doc_id=doc.doc_id,
        title=doc.title,
        source=doc.source,
        chunks=chunks,
        status="indexed",
    )


@router.post("/query")
async def query(
    req: QueryRequest,
    request: Request,
    user: User = Depends(get_current_user),
):
    await validate_csrf(request, user)
    log.info("api_query", question=req.question[:80], user=user.sub)
    return await rag.query(req.question, req.top_k)


@router.get("/stats")
async def stats(user: User = Depends(get_current_user)):
    from .vector_store import store
    return {"total_vectors": await store.count, "status": "ok"}


@router.get("/documents")
async def list_documents(user: User = Depends(get_current_user)):
    from .vector_store import store
    doc_ids = await store.get_doc_ids()
    return {"documents": sorted(doc_ids), "count": len(doc_ids)}


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str, user: User = Depends(get_current_user)):
    from .vector_store import store
    chunks = await store.get_document_chunks(doc_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "doc_id": doc_id,
        "chunks": [
            {
                "chunk_id": chunk["id"],
                "index": chunk["metadata"].get("chunk_index", 0),
                "text": chunk["text"][:500],
                "metadata": chunk["metadata"],
            }
            for chunk in chunks
        ],
        "total_chunks": len(chunks),
    }


@router.get("/export")
async def export_knowledge_base(user: User = Depends(require_role("operator"))):
    """Export requires operator role."""
    from .vector_store import store
    doc_ids = await store.get_doc_ids()
    docs: dict[str, list[dict]] = {}
    for doc_id in doc_ids:
        chunks = await store.get_document_chunks(doc_id)
        docs[doc_id] = [
            {
                "chunk_id": chunk["id"],
                "index": chunk["metadata"].get("chunk_index", 0),
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            }
            for chunk in chunks
        ]
    return {
        "exported_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "total_documents": len(docs),
        "total_vectors": await store.count,
        "documents": docs,
    }


# Import secrets at top level for login endpoint
import secrets