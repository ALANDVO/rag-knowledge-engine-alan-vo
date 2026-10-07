"""RAG Knowledge Engine - FastAPI app."""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routes import router
from middleware import register_middleware

settings = get_settings()
structlog.configure(json_serializer=lambda e: __import__("json").dumps(e, default=str))

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
