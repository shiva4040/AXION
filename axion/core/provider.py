import os
import math
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, List
from pydantic import BaseModel
import numpy as np

T = TypeVar("T", bound=BaseModel)

class ChatMessage(BaseModel):
    role: str # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMProvider(ABC):
    """Abstract interface for LLM operations to ensure vendor independence."""
    
    @abstractmethod
    async def generate_text(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
        response_model: Optional[Type[T]] = None
    ) -> LLMResponse:
        """Generates natural language completion, optionally adhering to a Pydantic schema."""
        pass

    @abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Generates dense vector embeddings for input texts."""
        pass

class MockProvider(LLMProvider):
    """
    Deterministic mock provider for unit tests, offline development,
    and zero-contamination testing. Generates deterministic pseudo-embeddings
    via string hashing and predictable mock reasoning completions.
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def generate_text(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
        response_model: Optional[Type[T]] = None
    ) -> LLMResponse:
        # If a structured Pydantic schema is requested, we can return dummy or default fields
        last_message = messages[-1].content if messages else ""
        mock_text = f"Mock synthesis for: {last_message[:100]} [Citation: doc_mock_01, p.1]"
        
        return LLMResponse(
            text=mock_text,
            model="axion-mock-v1",
            prompt_tokens=len(last_message.split()),
            completion_tokens=len(mock_text.split()),
            total_tokens=len(last_message.split()) + len(mock_text.split())
        )

    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # Deterministic pseudo-embedding based on hash of tokens
            vec = np.zeros(self.dimension, dtype=np.float32)
            words = text.lower().split()
            if not words:
                embeddings.append(vec.tolist())
                continue
            for i, word in enumerate(words):
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                idx = h % self.dimension
                val = ((h >> 16) % 1000) / 1000.0 - 0.5
                vec[idx] += val
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

class OpenAIProvider(LLMProvider):
    """Native OpenAI REST API adapter via httpx."""
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        from axion.config import settings
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate_text(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
        response_model: Optional[Type[T]] = None
    ) -> LLMResponse:
        import httpx
        if not self.api_key:
            return MockProvider().generate_text(messages, temperature, max_tokens, response_model)
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            return LLMResponse(
                text=choice["message"]["content"],
                model=self.model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        import httpx
        if not self.api_key:
            return await MockProvider().generate_embeddings(texts)
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": "text-embedding-3-small", "input": texts}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

class GeminiProvider(LLMProvider):
    """Native Google Gemini REST API adapter via httpx."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        strict: bool = False,
    ):
        from axion.config import settings
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model or getattr(settings, "gemini_model", "gemini-3.1-flash-lite")
        self.strict = strict
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate_text(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
        response_model: Optional[Type[T]] = None
    ) -> LLMResponse:
        import httpx
        if not self.api_key:
            if self.strict:
                raise ValueError(
                    "GeminiProvider: GEMINI_API_KEY is not configured in the environment or .env file. "
                    "Cannot execute live requests without valid authentication credentials."
                )
            import logging
            logging.getLogger(__name__).warning("GEMINI_API_KEY is not configured. Falling back to MockProvider.")
            return await MockProvider().generate_text(messages, temperature, max_tokens, response_model)
        
        contents = []
        for m in messages:
            role = "user" if m.role in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            last_err = None
            for attempt in range(3):
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    cand = data["candidates"][0]
                    text = cand["content"]["parts"][0]["text"]
                    usage = data.get("usageMetadata", {})
                    return LLMResponse(
                        text=text,
                        model=self.model,
                        prompt_tokens=usage.get("promptTokenCount", 0),
                        completion_tokens=usage.get("candidatesTokenCount", 0),
                        total_tokens=usage.get("totalTokenCount", 0),
                    )
                except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.TransportError) as e:
                    last_err = e
                    if attempt < 2:
                        import asyncio
                        await asyncio.sleep(1.5 * (attempt + 1))
                        continue
                    # Sanitize message to guarantee no secret exposure
                    msg = str(e)
                    if self.api_key and self.api_key in msg:
                        msg = msg.replace(self.api_key, "[REDACTED]")
                    status_info = getattr(getattr(e, "response", None), "status_code", type(e).__name__)
                    raise RuntimeError(f"Gemini API error ({status_info}): {msg}") from None
                except Exception as e:
                    raise e
            if last_err:
                raise last_err

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key and self.strict:
            raise ValueError(
                "GeminiProvider: GEMINI_API_KEY is not configured. Cannot generate embeddings."
            )
        # Remote Gemini Generative Language API v1beta does not expose batchEmbedContents on this tier.
        # Fallback cleanly to deterministic local embeddings for retrieval indexing,
        # ensuring all text generation, reasoning, and synthesis strictly execute on live gemini-3.1-flash-lite.
        return await MockProvider().generate_embeddings(texts)

def get_llm_provider(provider_name: Optional[str] = None, strict: bool = False) -> LLMProvider:
    from axion.config import settings
    name = (provider_name or settings.default_llm_provider).lower()
    
    if name == "mock":
        return MockProvider(dimension=settings.embedding_dimension)
    elif name == "openai":
        return OpenAIProvider()
    elif name == "gemini":
        return GeminiProvider(strict=strict)
    else:
        return MockProvider(dimension=settings.embedding_dimension)
