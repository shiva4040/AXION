from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from axion.core.provider import LLMProvider, ChatMessage, get_llm_provider
from axion.baseline.retriever import RetrievedChunk

class Citation(BaseModel):
    document_id: str
    document_title: str
    page_number: int
    chunk_id: str

class BaselineAnswer(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    retrieved_chunks_count: int
    abstained: bool = False

class BaselineGenerator:
    """
    Component 3 Subsystem:
    Generates evidence-backed answers from retrieved chunks using conventional RAG.
    """
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_llm_provider()

    async def generate_answer(
        self,
        query: str,
        chunks: List[RetrievedChunk]
    ) -> BaselineAnswer:
        """
        Synthesizes an answer using ONLY provided chunks, or abstains if insufficient.
        """
        if not chunks:
            return BaselineAnswer(
                query=query,
                answer="Insufficient evidence in the ingested documents to answer this question.",
                citations=[],
                retrieved_chunks_count=0,
                abstained=True
            )

        context_blocks = []
        citations: List[Citation] = []
        for i, c in enumerate(chunks):
            header_str = f" ({c.structural_header})" if c.structural_header else ""
            context_blocks.append(
                f"[Source {i+1}: {c.document_title}, Page {c.page_number}{header_str}]\n{c.text_content}"
            )
            citations.append(
                Citation(
                    document_id=c.document_id,
                    document_title=c.document_title,
                    page_number=c.page_number,
                    chunk_id=c.chunk_id
                )
            )

        context_text = "\n\n---\n\n".join(context_blocks)
        prompt = f"""
You are the AXION Research Assistant Baseline system.
Answer the following user question using ONLY the primary source excerpts provided below.
Rules:
1. Ground every statement in the provided sources.
2. Cite sources in brackets like [{chunks[0].document_title}, p.{chunks[0].page_number}].
3. If the provided excerpts do not contain sufficient facts to answer the question, state clearly that the evidence is insufficient.
4. Do not invent formulas, numbers, or external facts.

Primary Source Excerpts:
{context_text}

User Question:
{query}
"""
        messages = [
            ChatMessage(role="system", content="You are a rigorous, evidence-grounded research assistant. Never hallucinate unsupported claims."),
            ChatMessage(role="user", content=prompt)
        ]

        resp = await self.provider.generate_text(messages=messages, temperature=0.0)

        # Check if model self-abstained
        abstained = any(phrase in resp.text.lower() for phrase in [
            "insufficient evidence", "not mentioned in the text", "cannot be answered"
        ])

        return BaselineAnswer(
            query=query,
            answer=resp.text,
            citations=citations,
            retrieved_chunks_count=len(chunks),
            abstained=abstained
        )
