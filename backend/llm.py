"""LLM client."""
import structlog
from config import get_settings

log = structlog.get_logger()


async def chat(messages: list[dict], temperature: float = 0.7) -> str:
    s = get_settings()
    log.info("llm_chat", model=s.llm_model, messages=len(messages))
    # Placeholder - real implementation calls LLM_API_KEY provider
    return "This is a generated answer based on the provided context."


async def embed(texts: list[str]) -> list[list[float]]:
    import hashlib
    s = get_settings()
    log.info("llm_embed", model=s.embedding_model, texts=len(texts))
    results = []
    for t in texts:
        h = hashlib.sha256(t.encode()).digest()
        vec = [b / 255.0 for b in h[:64]]
        results.append(vec)
    return results
