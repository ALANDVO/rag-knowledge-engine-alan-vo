"""LLM client with multi-provider support."""
import hashlib
import os
import structlog
from typing import Literal
import httpx
from .config import get_settings

log = structlog.get_logger()


ProviderType = Literal["openai", "anthropic", "gemini", "ollama", "mock"]


class LLMClient:
    """Multi-provider LLM client."""

    def __init__(self):
        self.settings = get_settings()
        self.provider = self._detect_provider()
        self.client = httpx.AsyncClient(timeout=60.0)

    def _detect_provider(self) -> ProviderType:
        base_url = os.getenv("LLM_BASE_URL", "").lower()
        if "anthropic" in base_url:
            return "anthropic"
        elif "gemini" in base_url or "generativelanguage" in base_url:
            return "gemini"
        elif "ollama" in base_url or base_url.startswith("http://localhost:11434"):
            return "ollama"
        elif os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "mock"

    async def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        log.info("llm_chat", provider=self.provider, model=self.settings.llm_model, messages=len(messages))

        if self.provider == "mock":
            return self._mock_chat(messages)

        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            log.warning("llm_chat_no_key", provider=self.provider)
            return self._mock_chat(messages)

        try:
            if self.provider == "openai":
                return await self._openai_chat(messages, temperature, api_key)
            elif self.provider == "anthropic":
                return await self._anthropic_chat(messages, temperature, api_key)
            elif self.provider == "gemini":
                return await self._gemini_chat(messages, temperature, api_key)
            elif self.provider == "ollama":
                return await self._ollama_chat(messages, temperature)
        except Exception as e:
            log.error("llm_chat_error", provider=self.provider, error=str(e))
            return f"[LLM Error: {type(e).__name__}]"

        return self._mock_chat(messages)

    async def _openai_chat(self, messages: list[dict], temperature: float, api_key: str) -> str:
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": self.settings.llm_model, "messages": messages, "temperature": temperature}
        resp = await self.client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    async def _anthropic_chat(self, messages: list[dict], temperature: float, api_key: str) -> str:
        base_url = os.getenv("LLM_BASE_URL", "https://api.anthropic.com/v1")
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]
        payload = {"model": self.settings.llm_model, "messages": user_msgs, "temperature": temperature}
        if system_msg:
            payload["system"] = system_msg
        resp = await self.client.post(f"{base_url}/messages", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    async def _gemini_chat(self, messages: list[dict], temperature: float, api_key: str) -> str:
        base_url = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages if m["role"] != "system"]
        payload = {"contents": contents, "generationConfig": {"temperature": temperature}}
        resp = await self.client.post(f"{base_url}/models/{self.settings.llm_model}:generateContent?key={api_key}", json=payload)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    async def _ollama_chat(self, messages: list[dict], temperature: float) -> str:
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        payload = {"model": self.settings.llm_model, "messages": messages, "stream": False, "options": {"temperature": temperature}}
        resp = await self.client.post(f"{base_url}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _mock_chat(self, messages: list[dict]) -> str:
        return "This is a generated answer based on the provided context. (Mock response)"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        log.info("llm_embed", provider=self.provider, model=self.settings.embedding_model, texts=len(texts))

        if self.provider == "mock":
            return self._mock_embed(texts)

        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._mock_embed(texts)

        try:
            if self.provider in ("openai", "ollama"):
                return await self._openai_embed(texts, api_key)
            elif self.provider == "gemini":
                return await self._gemini_embed(texts, api_key)
        except Exception as e:
            log.error("llm_embed_error", provider=self.provider, error=str(e))

        return self._mock_embed(texts)

    async def _openai_embed(self, texts: list[str], api_key: str) -> list[list[float]]:
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": self.settings.embedding_model, "input": texts}
        resp = await self.client.post(f"{base_url}/embeddings", headers=headers, json=payload)
        resp.raise_for_status()
        return [d["embedding"] for d in resp.json()["data"]]

    async def _gemini_embed(self, texts: list[str], api_key: str) -> list[list[float]]:
        base_url = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        results = []
        for t in texts:
            payload = {"model": self.settings.embedding_model, "content": {"parts": [{"text": t}]}}
            resp = await self.client.post(f"{base_url}/models/{self.settings.embedding_model}:embedContent?key={api_key}", json=payload)
            resp.raise_for_status()
            results.append(resp.json()["embedding"]["values"])
        return results

    def _mock_embed(self, texts: list[str]) -> list[list[float]]:
        results = []
        for t in texts:
            h = hashlib.sha512(t.encode()).digest()
            vec = [b / 255.0 for b in h[:64]]
            results.append(vec)
        return results

    async def close(self):
        await self.client.aclose()


_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


async def chat(messages: list[dict], temperature: float = 0.7) -> str:
    return await get_client().chat(messages, temperature)


async def embed(texts: list[str]) -> list[list[float]]:
    return await get_client().embed(texts)
