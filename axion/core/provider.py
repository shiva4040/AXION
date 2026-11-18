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

def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    from axion.config import settings
    name = (provider_name or settings.default_llm_provider).lower()
    
    if name == "mock":
        return MockProvider(dimension=settings.embedding_dimension)
    elif name == "openai":
        # Lazy import of openai adapter
        from axion.core.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif name == "gemini":
        # Lazy import of gemini adapter
        from axion.core.gemini_provider import GeminiProvider
        return GeminiProvider()
    else:
        # Default fallback to Mock
        return MockProvider(dimension=settings.embedding_dimension)
