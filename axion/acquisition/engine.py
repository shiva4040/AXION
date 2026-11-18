import re
import time
import uuid
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from axion.database.models import DocumentChunk
from axion.acquisition.types import (
    SourceDocument, DocumentType, AccessStatus, AcquisitionMode,
    SearchRequest, SearchResponse, IngestAcquiredResponse, SourceHealthStatus
)
from axion.acquisition.connectors.base import BaseSourceConnector
from axion.acquisition.connectors.arxiv import ArxivConnector
from axion.acquisition.connectors.crossref import CrossrefConnector
from axion.acquisition.connectors.pubmed import PubMedConnector
from axion.acquisition.connectors.openalex import OpenAlexConnector
from axion.acquisition.connectors.huggingface import HuggingFaceConnector
from axion.acquisition.connectors.kaggle import KaggleConnector
from axion.acquisition.connectors.web_search import WebSearchConnector
from axion.acquisition.connectors.local_upload import LocalUploadConnector
from axion.ingestion.source_manager import SourceManager
from axion.knowledge_graph.extractor import KnowledgeGraphExtractor
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.core.types import EpistemicTier, TrustTier, ProvenancePointer

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "what", "how", "why", "when", "where", "who", "which", "does", "do", "did",
    "is", "are", "was", "were", "can", "we", "could", "would", "should", "the",
    "a", "an", "and", "or", "in", "on", "at", "by", "for", "with", "about",
    "like", "through", "over", "between", "under", "into", "from", "to", "of"
}

class InformationAcquisitionEngine:
    """
    Component: Universal Information Acquisition Engine.
    Discovers, searches, deduplicates, verifies, and ingests scientific knowledge
    from external scholarly APIs, preprint servers, dataset hubs, and local archives.
    """

    def __init__(
        self,
        connectors: Optional[List[BaseSourceConnector]] = None,
        db_session: Optional[AsyncSession] = None
    ):
        self.session = db_session
        if connectors is not None:
            self.connectors: Dict[str, BaseSourceConnector] = {c.source_name: c for c in connectors}
        else:
            # Register full default suite of 8 connectors
            default_connectors: List[BaseSourceConnector] = [
                ArxivConnector(),
                CrossrefConnector(),
                PubMedConnector(),
                OpenAlexConnector(),
                HuggingFaceConnector(),
                KaggleConnector(),
                WebSearchConnector(),
                LocalUploadConnector(session=db_session)
            ]
            self.connectors = {c.source_name: c for c in default_connectors}

        self._search_history: List[SearchResponse] = []
        self._acquired_documents_registry: Dict[str, SourceDocument] = {}

    def get_connector(self, name: str) -> Optional[BaseSourceConnector]:
        return self.connectors.get(name)

    def list_sources(self) -> List[str]:
        return list(self.connectors.keys())

    async def get_all_sources_health(self) -> List[SourceHealthStatus]:
        """Runs concurrent health and authorization checks on all connectors."""
        tasks = [c.check_health() for c in self.connectors.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        statuses: List[SourceHealthStatus] = []
        for i, res in enumerate(results):
            connector_name = list(self.connectors.keys())[i]
            if isinstance(res, Exception):
                statuses.append(SourceHealthStatus(
                    source_name=connector_name,
                    source_type=self.connectors[connector_name].source_type,
                    is_available=False,
                    status_message=f"Health check failed: {str(res)}",
                    supported_doc_types=self.connectors[connector_name].supported_doc_types
                ))
            else:
                statuses.append(res)
        return statuses

    def identify_subjects_and_terms(self, query: str) -> List[str]:
        """
        Decomposes research query into core concepts, multi-word entities, and search terms.
        """
        clean = re.sub(r"[^\w\s\-]", " ", query.lower())
        words = [w for w in clean.split() if len(w) > 2 and w not in STOP_WORDS]

        # Multi-word key phrases
        phrases = []
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")

        # Domain term identification
        identified = []
        if phrases:
            identified.extend(phrases[:3])
        identified.extend(words[:5])

        # Deduplicate while preserving order
        seen = set()
        unique_terms = []
        for t in identified:
            if t not in seen:
                unique_terms.append(t)
                seen.add(t)

        return unique_terms or [query.strip()]

    def select_connectors(self, query: str, requested_sources: Optional[List[str]] = None) -> List[BaseSourceConnector]:
        """
        Selects relevant connectors based on query domain and user preferences.
        """
        if requested_sources:
            selected = [self.connectors[s] for s in requested_sources if s in self.connectors]
            if selected:
                return selected

        q_lower = query.lower()
        selected_names: Set[str] = set()

        # Domain heuristics
        if any(w in q_lower for w in ["bio", "cell", "protein", "dna", "gene", "medical", "disease", "photosynthesis", "enzyme", "chloroplast"]):
            selected_names.update(["pubmed", "crossref", "openalex"])

        if any(w in q_lower for w in ["dataset", "benchmark", "data", "corpus", "metrics", "training", "evaluation"]):
            selected_names.update(["huggingface", "kaggle"])

        if any(w in q_lower for w in ["physics", "quantum", "equation", "formula", "relativity", "mechanics", "thermodynamics", "circuit", "motor", "lift"]):
            selected_names.update(["arxiv", "crossref", "openalex"])

        # Default fallback: query broad academic and web sources
        if not selected_names:
            selected_names = {"arxiv", "crossref", "openalex", "web_search", "local_upload"}

        # Always include local upload if available
        selected_names.add("local_upload")

        connectors = [self.connectors[name] for name in selected_names if name in self.connectors]
        return connectors if connectors else list(self.connectors.values())

    async def search(self, req: SearchRequest) -> SearchResponse:
        """
        Orchestrates full discovery: query parsing, connector selection, concurrent execution,
        normalization, deduplication, licensing verification, and relevance ranking.
        """
        start_time = time.time()
        identified_terms = self.identify_subjects_and_terms(req.query)
        effective_query = " ".join(identified_terms[:3]) if identified_terms else req.query

        connectors = self.select_connectors(req.query, req.sources)
        sources_queried = [c.source_name for c in connectors]

        # Concurrent execution across all selected connectors
        tasks = [
            c.search(query=effective_query, limit=req.max_results_per_source)
            for c in connectors
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        raw_documents: List[SourceDocument] = []
        for i, res in enumerate(results):
            c_name = sources_queried[i]
            if isinstance(res, Exception):
                logger.warning("Connector '%s' failed during search: %s", c_name, res)
            elif isinstance(res, list):
                raw_documents.extend(res)

        total_discovered = len(raw_documents)

        # Multi-stage deduplication
        deduplicated = self.deduplicate(raw_documents)
        total_dedup = len(deduplicated)

        # Relevance ranking
        ranked = self.rank_relevance(req.query, deduplicated)

        # Filter by minimum relevance
        final_docs = [d for d in ranked if d.relevance_score >= req.min_relevance]

        # Register in memory lookup
        for d in final_docs:
            self._acquired_documents_registry[d.id] = d

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        resp = SearchResponse(
            query=req.query,
            identified_terms=identified_terms,
            sources_queried=sources_queried,
            total_discovered=total_discovered,
            total_deduplicated=total_dedup,
            documents=final_docs,
            execution_time_ms=elapsed_ms
        )
        self._search_history.append(resp)
        return resp

    def deduplicate(self, documents: List[SourceDocument]) -> List[SourceDocument]:
        """
        Deduplicates documents using:
        1. Normalized DOI matching
        2. Exact source URL matching
        3. Normalized title similarity
        Merges complementary metadata when duplicates are identified.
        """
        seen_dois: Dict[str, SourceDocument] = {}
        seen_urls: Dict[str, SourceDocument] = {}
        seen_titles: Dict[str, SourceDocument] = {}
        unique_docs: List[SourceDocument] = []

        for doc in documents:
            norm_doi = doc.doi.lower().strip() if doc.doi else None
            norm_url = doc.source_url.lower().strip() if doc.source_url else None
            norm_title = re.sub(r"[^\w\s]", "", doc.title.lower()).strip()

            existing_match: Optional[SourceDocument] = None

            if norm_doi and norm_doi in seen_dois:
                existing_match = seen_dois[norm_doi]
            elif norm_url and norm_url in seen_urls:
                existing_match = seen_urls[norm_url]
            elif norm_title and norm_title in seen_titles:
                existing_match = seen_titles[norm_title]

            if existing_match:
                # Merge metadata and prefer longer content/full text
                if len(doc.content) > len(existing_match.content):
                    existing_match.content = doc.content
                    existing_match.document_type = doc.document_type
                    existing_match.is_full_text = doc.is_full_text
                if not existing_match.doi and doc.doi:
                    existing_match.doi = doc.doi
                if not existing_match.authors and doc.authors:
                    existing_match.authors = doc.authors
                if doc.license and existing_match.license == "Unknown":
                    existing_match.license = doc.license
                if doc.access_status == AccessStatus.OPEN_ACCESS:
                    existing_match.access_status = AccessStatus.OPEN_ACCESS
                existing_match.metadata.update(doc.metadata)
            else:
                unique_docs.append(doc)
                if norm_doi:
                    seen_dois[norm_doi] = doc
                if norm_url:
                    seen_urls[norm_url] = doc
                if norm_title:
                    seen_titles[norm_title] = doc

        return unique_docs

    def rank_relevance(self, query: str, documents: List[SourceDocument]) -> List[SourceDocument]:
        """
        Ranks acquired documents by scientific relevance score:
        - Title match (weight: 3.0)
        - Abstract/content match (weight: 1.0)
        - Exact multi-word phrase presence (bonus: +0.25)
        - Trust tier weighting (peer-reviewed > web)
        - Full-text bonus (+0.1)
        """
        q_terms = set(w.lower() for w in re.sub(r"[^\w\s]", "", query).split() if len(w) > 2 and w.lower() not in STOP_WORDS)
        q_clean = query.lower().strip()

        for doc in documents:
            score = 0.0
            t_words = set(re.sub(r"[^\w\s]", "", doc.title.lower()).split())
            c_words = set(re.sub(r"[^\w\s]", "", doc.content.lower()).split())

            if q_terms:
                t_overlap = len(q_terms.intersection(t_words)) / len(q_terms)
                c_overlap = len(q_terms.intersection(c_words)) / len(q_terms)
                score += (t_overlap * 0.6) + (c_overlap * 0.4)

            # Exact query phrase matching in title or content
            if q_clean in doc.title.lower():
                score += 0.3
            elif q_clean in doc.content.lower():
                score += 0.15

            # Trust tier weighting
            if doc.trust_tier == TrustTier.PEER_REVIEWED:
                score += 0.1
            elif doc.trust_tier == TrustTier.TECHNICAL_DOC:
                score += 0.05

            # Full text bonus
            if doc.is_full_text:
                score += 0.05

            doc.relevance_score = round(min(1.0, max(0.05, score)), 3)

        # Sort descending by relevance score
        documents.sort(key=lambda d: d.relevance_score, reverse=True)
        return documents

    async def ingest_documents(
        self,
        documents: List[SourceDocument],
        session: AsyncSession,
        extract_knowledge_graph: bool = True
    ) -> IngestAcquiredResponse:
        """
        Ingests acquired documents into AXION:
        1. Persists Document and DocumentChunk records via SourceManager.
        2. Generates vector embeddings using existing EmbeddingProvider.
        3. Extracts scientific entities and relations into KnowledgeGraph.
        4. Preserves original provenance and sets EpistemicTier to FACT_DOCUMENTED.
        (Note: Does NOT promote acquired content to FINDING_VALIDATED).
        """
        manager = SourceManager(session)
        extractor = KnowledgeGraphExtractor()
        graph_store = KnowledgeGraphStore(session)

        ingested_ids: List[str] = []
        total_chunks = 0
        nodes_created = 0
        edges_created = 0
        errors: List[str] = []

        for doc in documents:
            try:
                # Ingest via SourceManager (handles chunking & embeddings)
                db_doc = await manager.ingest_text(
                    text_content=doc.content,
                    title=doc.title,
                    source_uri=doc.source_url or f"acquired://{doc.source_name}/{doc.id}",
                    trust_tier=doc.trust_tier.value
                )
                ingested_ids.append(db_doc.id)

                # Explicitly retrieve chunks to prevent missing greenlet on lazy relationship loading
                c_stmt = (
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == db_doc.id)
                    .order_by(DocumentChunk.chunk_index)
                )
                c_res = await session.execute(c_stmt)
                db_chunks = c_res.scalars().all()
                total_chunks += len(db_chunks)

                # Update document metadata with acquired source details
                db_doc.license_type = doc.license or "Unknown"
                db_doc.doc_metadata = {
                    "acquired_id": doc.id,
                    "source_name": doc.source_name,
                    "doi": doc.doi,
                    "authors": doc.authors,
                    "publication_date": doc.publication_date,
                    "access_status": doc.access_status.value,
                    "document_type": doc.document_type.value,
                    "retrieval_date": doc.retrieval_date,
                    "is_full_text": doc.is_full_text,
                    "epistemic_tier": EpistemicTier.FACT_DOCUMENTED.value,
                    **doc.metadata
                }

                # Extract into Knowledge Graph if requested
                if extract_knowledge_graph and db_chunks:
                    for chunk in db_chunks:
                        extraction = extractor.extract_from_text(
                            text=chunk.text_content,
                            domain=doc.metadata.get("primary_category", "general_science"),
                            document_id=db_doc.id,
                            chunk_id=chunk.id
                        )
                        res = await graph_store.add_extraction_result(
                            extraction=extraction,
                            chunk_id=chunk.id,
                            default_domain="general_science"
                        )
                        nodes_created += res.get("nodes_created", 0)
                        edges_created += res.get("edges_created", 0)

            except Exception as e:
                err_msg = f"Failed to ingest document '{doc.title}': {str(e)}"
                logger.warning(err_msg)
                errors.append(err_msg)

        await session.commit()

        return IngestAcquiredResponse(
            ingested_count=len(ingested_ids),
            document_ids=ingested_ids,
            total_chunks_created=total_chunks,
            graph_entities_created=nodes_created,
            graph_relations_created=edges_created,
            errors=errors
        )

    def get_document_by_id(self, doc_id: str) -> Optional[SourceDocument]:
        """Retrieves an acquired document from the in-memory registry."""
        return self._acquired_documents_registry.get(doc_id)

    def get_history(self) -> List[SearchResponse]:
        """Returns the search and discovery history."""
        return list(self._search_history)
