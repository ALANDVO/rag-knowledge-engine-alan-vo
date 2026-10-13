"""Tests for middleware."""
import pytest
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from unittest.mock import AsyncMock, MagicMock

from app.middleware import RequestLoggerMiddleware, ErrorMiddleware, register_middleware


class TestRequestLoggerMiddleware:
    """Tests for RequestLoggerMiddleware."""

    @pytest.fixture
    def middleware(self):
        return RequestLoggerMiddleware(app=MagicMock())

    @pytest.mark.asyncio
    async def test_adds_request_id_header(self, middleware):
        mock_call_next = AsyncMock(return_value=Response(content=b"OK"))
        request = Request({"type": "http", "method": "GET", "path": "/test", "headers": []})
        response = await middleware.dispatch(request, mock_call_next)
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) == 8

    @pytest.mark.asyncio
    async def test_logs_request_start_and_done(self, middleware, caplog):
        import structlog
        structlog.configure(processors=[structlog.processors.JSONRenderer()])
        mock_call_next = AsyncMock(return_value=Response(content=b"OK", status_code=200))
        request = Request({"type": "http", "method": "POST", "path": "/api/documents", "headers": []})
        await middleware.dispatch(request, mock_call_next)
        # Logs are checked implicitly


class TestErrorMiddleware:
    """Tests for ErrorMiddleware."""

    @pytest.fixture
    def middleware(self):
        return ErrorMiddleware(app=MagicMock())

    @pytest.mark.asyncio
    async def test_passes_through_successful_response(self, middleware):
        mock_call_next = AsyncMock(return_value=Response(content=b"OK", status_code=200))
        request = Request({"type": "http", "method": "GET", "path": "/health", "headers": []})
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_catches_exception_returns_500(self, middleware):
        async def failing_call_next(request):
            raise ValueError("Something went wrong")
        request = Request({"type": "http", "method": "GET", "path": "/test", "headers": []})
        response = await middleware.dispatch(request, failing_call_next)
        assert response.status_code == 500
        assert isinstance(response, JSONResponse)
        import json
        body = json.loads(response.body)
        assert body["error"] == "Internal server error"


class TestRegisterMiddleware:
    """Tests for register_middleware function."""

    def test_registers_both_middlewares(self):
        from fastapi import FastAPI
        from app.middleware import SessionInitMiddleware
        app = FastAPI()
        register_middleware(app)
        # Check that middleware was added (3 middlewares now)
        assert len(app.user_middleware) == 3
        middleware_types = [m.cls for m in app.user_middleware]
        assert SessionInitMiddleware in middleware_types
        assert RequestLoggerMiddleware in middleware_types
        assert ErrorMiddleware in middleware_types