from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import DocumentChunk, Document
from axion.core.provider import LLMProvider, get_llm_provider

import re
from typing import List, Dict, Any, Optional
import numpy as np
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import DocumentChunk, Document
from axion.core.provider import LLMProvider, get_llm_provider

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
    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        provider: Optional[LLMProvider] = None,
        corpus_chunks: Optional[List[RetrievedChunk]] = None,
    ):
        self.session = db_session
        self.provider = provider or get_llm_provider()
        self.corpus_chunks = corpus_chunks or []
        self._chunk_embeddings: Dict[str, List[float]] = {}

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

    @staticmethod
    def _lexical_similarity(query: str, text: str) -> float:
        """Computes basic Jaccard word overlap as fallback similarity."""
        q_words = set(re.findall(r"\w+", query.lower()))
        t_words = set(re.findall(r"\w+", text.lower()))
        if not q_words or not t_words:
            return 0.0
        intersection = q_words.intersection(t_words)
        return float(len(intersection) / len(q_words))

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.20
    ) -> List[RetrievedChunk]:
        """
        Generates query embedding and returns top-k nearest document chunks.
        """
        query_embeddings = await self.provider.generate_embeddings([query])
        q_vec = query_embeddings[0] if (query_embeddings and query_embeddings[0]) else []

        scored_chunks: List[RetrievedChunk] = []

        # 1. In-memory corpus chunks path (for benchmark experiments)
        if self.corpus_chunks:
            # Batch generate embeddings for corpus chunks if not cached
            uncached = [c for c in self.corpus_chunks if c.chunk_id not in self._chunk_embeddings]
            if uncached and q_vec:
                chunk_texts = [c.text_content for c in uncached]
                emb_list = await self.provider.generate_embeddings(chunk_texts)
                for c, emb in zip(uncached, emb_list):
                    self._chunk_embeddings[c.chunk_id] = emb

            for c in self.corpus_chunks:
                sim = 0.0
                c_emb = self._chunk_embeddings.get(c.chunk_id)
                if q_vec and c_emb:
                    sim = self._cosine_similarity(q_vec, c_emb)
                # Combine or fallback with lexical overlap if embedding similarity is 0
                lex = self._lexical_similarity(query, c.text_content)
                effective_sim = max(sim, lex)
                if effective_sim >= min_similarity:
                    scored_chunks.append(
                        RetrievedChunk(
                            chunk_id=c.chunk_id,
                            document_id=c.document_id,
                            document_title=c.document_title,
                            page_number=c.page_number,
                            text_content=c.text_content,
                            structural_header=c.structural_header,
                            similarity_score=round(effective_sim, 4)
                        )
                    )

        # 2. Database session path
        elif self.session:
            stmt = (
                select(DocumentChunk, Document.title)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(DocumentChunk.embedding.isnot(None))
            )
            res = await self.session.execute(stmt)
            rows = res.all()

            for chunk, doc_title in rows:
                if not chunk.embedding:
                    continue
                sim = self._cosine_similarity(q_vec, chunk.embedding) if q_vec else 0.0
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
