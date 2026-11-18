import time
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from axion.core.provider import LLMProvider, get_llm_provider
from axion.baseline.retriever import BaselineRetriever, RetrievedChunk
from axion.baseline.generator import BaselineGenerator, BaselineAnswer, Citation

class BaselineResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    retrieved_chunks: List[RetrievedChunk]
    execution_time_ms: int
    abstained: bool

class BaselineController:
    """
    Component 3 Controller:
    The conventional RAG research assistant baseline.
    Acts as the experimental control group for research benchmark evaluations.
    """
    def __init__(self, db_session: AsyncSession, provider: Optional[LLMProvider] = None):
        self.session = db_session
        self.provider = provider or get_llm_provider()
        self.retriever = BaselineRetriever(db_session, self.provider)
        self.generator = BaselineGenerator(self.provider)

    async def query(
        self,
        query_text: str,
        top_k: int = 5,
        min_similarity: float = 0.20
    ) -> BaselineResponse:
        """
        Executes conventional RAG: retrieve top-k chunks -> prompt LLM -> return answer with citations.
        """
        t0 = time.time()
        
        # 1. Retrieve
        chunks = await self.retriever.retrieve(
            query=query_text,
            top_k=top_k,
            min_similarity=min_similarity
        )

        # 2. Generate
        result: BaselineAnswer = await self.generator.generate_answer(
            query=query_text,
            chunks=chunks
        )
        
        t1 = time.time()
        duration_ms = int((t1 - t0) * 1000)

        return BaselineResponse(
            query=query_text,
            answer=result.answer,
            citations=result.citations,
            retrieved_chunks=chunks,
            execution_time_ms=duration_ms,
            abstained=result.abstained
        )
