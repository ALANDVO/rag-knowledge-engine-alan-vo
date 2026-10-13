"""RAG Knowledge Engine - FastAPI app."""
import json
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routes import router
from .middleware import register_middleware

settings = get_settings()
def json_serializer(obj, **kwargs):
    # structlog passes its own default handler; prefer ours for non-serializable objects
    kwargs.pop("default", None)
    return json.dumps(obj, default=str, **kwargs)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(serializer=json_serializer),
    ]
)

app = FastAPI(
    title="RAG Knowledge Engine",
    version="1.0.0",
    description="Enterprise-grade Retrieval-Augmented Generation platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middleware(app)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
