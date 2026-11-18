from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import DocumentChunk, Document
from axion.core.provider import LLMProvider, get_llm_provider

class RetrievedChunk(BaseModel := type("BaseModel", (), {})):
    pass

from pydantic import BaseModel

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    page_number: int
    text_content: str
    structural_header: Optional[str] = None
    similarity_score: float

class BaselineRetriever:
    """
    Component 3 Subsystem:
    Dense vector semantic retriever serving as the experimental control baseline.
    Operates strictly without knowledge graphs or cross-domain multi-hop engines.
    """
    def __init__(self, db_session: AsyncSession, provider: Optional[LLMProvider] = None):
        self.session = db_session
        self.provider = provider or get_llm_provider()

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Computes cosine similarity between two vector lists."""
        a = np.array(vec1, dtype=np.float32)
        b = np.array(vec2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.25
    ) -> List[RetrievedChunk]:
        """
        Generates query embedding and returns top-k nearest document chunks.
        """
        query_embeddings = await self.provider.generate_embeddings([query])
        if not query_embeddings or not query_embeddings[0]:
            return []
        q_vec = query_embeddings[0]

        # Retrieve all chunks that have embeddings
        stmt = (
            select(DocumentChunk, Document.title)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(DocumentChunk.embedding.isnot(None))
        )
        res = await self.session.execute(stmt)
        rows = res.all()

        scored_chunks: List[RetrievedChunk] = []
        for chunk, doc_title in rows:
            if not chunk.embedding:
                continue
            sim = self._cosine_similarity(q_vec, chunk.embedding)
            if sim >= min_similarity:
                scored_chunks.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        document_title=doc_title,
                        page_number=chunk.page_number,
                        text_content=chunk.text_content,
                        structural_header=chunk.structural_header,
                        similarity_score=round(sim, 4)
                    )
                )

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x.similarity_score, reverse=True)
        return scored_chunks[:top_k]
