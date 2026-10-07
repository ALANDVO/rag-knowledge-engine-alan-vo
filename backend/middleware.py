"""Shared middleware."""
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        req_id = str(uuid.uuid4())[:8]
        log.info("request_start", method=request.method, path=request.url.path)
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        log.info("request_done", path=request.url.path, status=response.status_code,
                 duration_ms=round(duration, 2), request_id=req_id)
        response.headers["X-Request-ID"] = req_id
        return response


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            log.exception("unhandled_error", path=request.url.path, error=str(e))
            from starlette.responses import JSONResponse
            return JSONResponse(status_code=500, content={"error": "Internal server error"})


def register_middleware(app):
    app.add_middleware(RequestLoggerMiddleware)
    app.add_middleware(ErrorMiddleware)
