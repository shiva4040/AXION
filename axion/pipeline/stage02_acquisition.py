import re
import time
import logging
from typing import Any, Dict, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from axion.core.provider import LLMProvider, get_llm_provider
from axion.core.types import BoundingBox, EpistemicTier, ProvenancePointer
from axion.database.models import Document, DocumentBoundingBox, DocumentChunk
from axion.baseline.retriever import BaselineRetriever
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.knowledge_memory.types import KnowledgeStatus, ValidatedFinding
from axion.acquisition.engine import InformationAcquisitionEngine
from axion.acquisition.types import SearchRequest
from axion.pipeline.types import AcquiredChunk, AcquisitionPayload, QuestionSpec

logger = logging.getLogger(__name__)


class KnowledgeAcquisitionCoordinator:
    """
    Stage 02: Knowledge Acquisition Coordinator.
    Coordinates local vector/document chunk retrieval, verified findings memory lookup,
    and optional external scholarly API discovery.
    Ensures every acquired chunk is stamped with verifiable ProvenancePointer metadata.
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        provider: Optional[LLMProvider] = None,
        acquisition_engine: Optional[InformationAcquisitionEngine] = None,
        memory: Optional[ValidatedKnowledgeMemory] = None,
        corpus_chunks: Optional[List[AcquiredChunk]] = None,
    ):
        self.session = db_session
        self.provider = provider
        self.acquisition_engine = acquisition_engine
        self.memory = memory
        self.corpus_chunks = corpus_chunks or []

    async def acquire_knowledge(
        self,
        question_spec: QuestionSpec,
        top_k: int = 5,
        min_similarity: float = 0.20,
        enable_external: bool = False,
        corpus_chunks: Optional[List[AcquiredChunk]] = None,
    ) -> AcquisitionPayload:
        """
        Executes Stage 02 knowledge acquisition across local DB, memory, and external sources.
        """
        t0 = time.time()
        retrieved_chunks: List[AcquiredChunk] = []
        candidate_memory_items: List[Dict[str, Any]] = []
        sources_queried: List[str] = []
        seen_chunk_keys: Set[str] = set()

        # 1. Attached document retrieval (explicit document focus)
        if question_spec.document_id and self.session:
            sources_queried.append("local_attached_document")
            try:
                stmt = (
                    select(DocumentChunk, Document.title)
                    .join(Document, DocumentChunk.document_id == Document.id)
                    .options(selectinload(DocumentChunk.bounding_boxes))
                    .where(DocumentChunk.document_id == question_spec.document_id)
                    .order_by(DocumentChunk.chunk_index)
                )
                res = await self.session.execute(stmt)
                rows = res.all()
                for chk, doc_title in rows[:top_k]:
                    chunk_key = f"{chk.document_id}:{chk.id}"
                    if chunk_key not in seen_chunk_keys:
                        seen_chunk_keys.add(chunk_key)
                        
                        bbox = None
                        if hasattr(chk, "bounding_boxes") and chk.bounding_boxes:
                            first_box = chk.bounding_boxes[0]
                            bbox = BoundingBox(
                                page_number=first_box.page_number,
                                x0=first_box.x0,
                                y0=first_box.y0,
                                x1=first_box.x1,
                                y1=first_box.y1
                            )
                        
                        prov = ProvenancePointer(
                            document_id=chk.document_id,
                            chunk_id=chk.id,
                            page_number=chk.page_number,
                            bounding_box=bbox,
                            extracted_snippet=chk.text_content[:300].strip()
                        )
                        
                        retrieved_chunks.append(AcquiredChunk(
                            chunk_id=chk.id,
                            document_id=chk.document_id,
                            page_number=chk.page_number,
                            text_content=chk.text_content,
                            similarity_score=1.0,
                            source_title=doc_title,
                            provenance=prov,
                            bounding_box=bbox
                        ))
            except Exception as e:
                logger.warning("Error acquiring attached document chunks: %s", e)

        # 2. In-memory corpus chunks (for evaluation benchmarks and test environments)
        all_corpus = list(self.corpus_chunks) + list(corpus_chunks or [])
        if all_corpus and len(retrieved_chunks) < top_k:
            sources_queried.append("in_memory_corpus")
            if question_spec.document_id:
                for c in all_corpus:
                    if c.document_id == question_spec.document_id:
                        chunk_key = f"{c.document_id}:{c.chunk_id}"
                        if chunk_key not in seen_chunk_keys:
                            seen_chunk_keys.add(chunk_key)
                            retrieved_chunks.append(c)

            if len(retrieved_chunks) < top_k:
                q_words = set(re.findall(r"\w+", question_spec.raw_query.lower()))
                scored = []
                for c in all_corpus:
                    chunk_key = f"{c.document_id}:{c.chunk_id}"
                    if chunk_key in seen_chunk_keys:
                        continue
                    c_words = set(re.findall(r"\w+", c.text_content.lower()))
                    score = len(q_words.intersection(c_words)) / max(len(q_words), 1)
                    if score >= min_similarity or len(retrieved_chunks) == 0:
                        scored.append((score, c))
                scored.sort(key=lambda x: x[0], reverse=True)
                for score, c in scored[:top_k - len(retrieved_chunks)]:
                    seen_chunk_keys.add(f"{c.document_id}:{c.chunk_id}")
                    retrieved_chunks.append(c)

        # 3. Local semantic vector retrieval across general database
        if self.session and len(retrieved_chunks) < top_k:
            sources_queried.append("local_vector_retriever")
            try:
                provider = self.provider or get_llm_provider()
                retriever = BaselineRetriever(self.session, provider)
                semantic_chunks = await retriever.retrieve(
                    query=question_spec.raw_query,
                    top_k=top_k,
                    min_similarity=min_similarity
                )
                for sc in semantic_chunks:
                    chunk_key = f"{sc.document_id}:{sc.chunk_id}"
                    if chunk_key not in seen_chunk_keys:
                        seen_chunk_keys.add(chunk_key)
                        prov = ProvenancePointer(
                            document_id=sc.document_id,
                            chunk_id=sc.chunk_id,
                            page_number=sc.page_number,
                            extracted_snippet=sc.text_content[:300].strip()
                        )
                        retrieved_chunks.append(AcquiredChunk(
                            chunk_id=sc.chunk_id,
                            document_id=sc.document_id,
                            page_number=sc.page_number,
                            text_content=sc.text_content,
                            similarity_score=sc.similarity_score,
                            source_title=sc.document_title,
                            provenance=prov
                        ))
            except Exception as e:
                logger.debug("Local semantic retrieval produced zero results or error: %s", e)

        # 3. Memory reading stub (Stage 07 integration)
        if self.memory:
            sources_queried.append("validated_knowledge_memory")
            try:
                active_findings: List[ValidatedFinding] = self.memory.list_findings(
                    status_filter=KnowledgeStatus.VALID
                )
                concepts_lower = [c.lower() for c in question_spec.extracted_concepts]
                domains_lower = [d.lower() for d in question_spec.domain_tags]

                for f in active_findings:
                    f_text = f"{f.title} {f.statement}".lower()
                    # Match by domain or concept overlap
                    domain_match = any(d in f_text for d in domains_lower)
                    concept_match = any(c in f_text for c in concepts_lower)
                    if domain_match or concept_match:
                        candidate_memory_items.append({
                            "finding_id": f.finding_id,
                            "title": f.title,
                            "statement": f.statement,
                            "epistemic_tier": f.epistemic_tier.value if hasattr(f.epistemic_tier, "value") else str(f.epistemic_tier),
                            "active_assumptions": f.active_assumptions,
                            "applicable_conditions": f.applicable_conditions,
                            "limitations": f.limitations,
                            "source_provenance": [
                                p.model_dump() if hasattr(p, "model_dump") else dict(p)
                                for p in f.source_provenance
                            ]
                        })
            except Exception as e:
                logger.warning("Error reading candidate memory findings: %s", e)

        # 4. Optional external scholarly acquisition
        if enable_external and self.acquisition_engine:
            sources_queried.append("external_acquisition_engine")
            try:
                req = SearchRequest(query=question_spec.raw_query, max_results_per_source=2)
                search_res = await self.acquisition_engine.search(req)
                for sdoc in search_res.documents:
                    doc_key = f"ext:{sdoc.source_name}:{sdoc.doi or sdoc.title}"
                    if doc_key not in seen_chunk_keys:
                        seen_chunk_keys.add(doc_key)
                        prov = ProvenancePointer(
                            document_id=sdoc.doi or sdoc.source_url or f"ext-{sdoc.source_name}",
                            chunk_id=f"chunk-{len(retrieved_chunks)}",
                            page_number=1,
                            extracted_snippet=sdoc.content[:300].strip()
                        )
                        retrieved_chunks.append(AcquiredChunk(
                            chunk_id=f"ext-chunk-{len(retrieved_chunks)}",
                            document_id=sdoc.doi or sdoc.source_url or f"ext-{sdoc.source_name}",
                            page_number=1,
                            text_content=sdoc.content,
                            similarity_score=sdoc.relevance_score,
                            source_title=sdoc.title,
                            source_uri=sdoc.source_url,
                            provenance=prov
                        ))
            except Exception as e:
                logger.warning("External acquisition lookup failed: %s", e)

        latency_ms = (time.time() - t0) * 1000.0

        return AcquisitionPayload(
            query_id=question_spec.query_id,
            retrieved_chunks=retrieved_chunks,
            candidate_memory_items=candidate_memory_items,
            sources_queried=sources_queried,
            total_retrieved=len(retrieved_chunks) + len(candidate_memory_items),
            acquisition_latency_ms=latency_ms,
            metadata={
                "top_k": top_k,
                "min_similarity": min_similarity,
                "enable_external": enable_external
            }
        )
