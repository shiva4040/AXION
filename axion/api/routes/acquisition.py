import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from axion.database.connection import get_db_session
from axion.acquisition.types import (
    SearchRequest,
    SearchResponse,
    IngestAcquiredRequest,
    IngestAcquiredResponse,
    SourceHealthStatus,
    SourceDocument,
    ContinuousSourceConfig,
)
from axion.acquisition.engine import InformationAcquisitionEngine
from axion.acquisition.continuous import ContinuousAcquisitionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/acquisition", tags=["Information Acquisition Engine"])

# Global engine and continuous manager instances
engine = InformationAcquisitionEngine()
continuous_manager = ContinuousAcquisitionManager()

@router.post("/search", response_model=SearchResponse)
async def search_external_sources(req: SearchRequest):
    """
    Core Discovery Endpoint:
    Discovers research literature, papers, datasets, and technical articles across
    arXiv, Crossref, PubMed, OpenAlex, Hugging Face, Kaggle, Web Search, and Local Archives.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    try:
        return await engine.search(req)
    except Exception as e:
        logger.exception("Acquisition search error for query '%s'", req.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/ingest", response_model=IngestAcquiredResponse)
async def ingest_acquired_documents(
    req: IngestAcquiredRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Information Processing & Ingestion Endpoint:
    Ingests acquired documents into AXION vector database and Knowledge Graph
    using the existing DocumentReader, DocumentChunker, EmbeddingProvider, and KnowledgeGraphStore.
    Preserves provenance and assigns EpistemicTier.FACT_DOCUMENTED.
    """
    docs_to_ingest: List[SourceDocument] = []

    # 1. Directly provided documents
    if req.documents:
        docs_to_ingest.extend(req.documents)

    # 2. Documents referenced by ID in registry
    if req.document_ids:
        for d_id in req.document_ids:
            doc = engine.get_document_by_id(d_id)
            if doc and doc not in docs_to_ingest:
                docs_to_ingest.append(doc)

    if not docs_to_ingest:
        raise HTTPException(
            status_code=400,
            detail="No valid documents provided or resolved for ingestion."
        )

    try:
        return await engine.ingest_documents(
            documents=docs_to_ingest,
            session=session,
            extract_knowledge_graph=req.extract_knowledge_graph
        )
    except Exception as e:
        logger.exception("Ingestion failed for acquired documents")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/sources", response_model=List[SourceHealthStatus])
async def list_available_sources():
    """
    Lists all configured source connectors and verifies their operational health,
    licensing restrictions, and API authorization status.
    """
    try:
        return await engine.get_all_sources_health()
    except Exception as e:
        logger.exception("Failed to check sources health")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/history", response_model=List[SearchResponse])
async def get_acquisition_history():
    """Retrieves search and acquisition history."""
    return engine.get_history()

@router.get("/documents/{document_id}", response_model=SourceDocument)
async def get_acquired_document(document_id: str):
    """Retrieves full metadata and content for a discovered document by ID."""
    doc = engine.get_document_by_id(document_id)
    if not doc:
        # Check connectors directly (e.g. arxiv or local)
        for connector in engine.connectors.values():
            try:
                fetched = await connector.get_document(document_id)
                if fetched:
                    return fetched
            except Exception:
                continue
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")
    return doc

# =========================================================================
# Continuous Acquisition Endpoints
# =========================================================================

@router.get("/subscriptions", response_model=List[ContinuousSourceConfig])
async def list_continuous_subscriptions():
    """Lists standing continuous topic subscriptions."""
    return continuous_manager.list_subscriptions()

@router.post("/subscriptions", response_model=ContinuousSourceConfig)
async def create_continuous_subscription(
    source_name: str = Query(..., description="Connector name or 'all'"),
    search_query: str = Query(..., description="Topic keywords to continuously track"),
    poll_interval_seconds: int = Query(3600, ge=60, description="Polling interval in seconds")
):
    """Registers a continuous topic for scheduled automated discovery."""
    return continuous_manager.add_subscription(
        source_name=source_name,
        search_query=search_query,
        poll_interval_seconds=poll_interval_seconds
    )

@router.post("/subscriptions/{config_id}/poll")
async def poll_subscription_now(
    config_id: str,
    auto_ingest: bool = Query(False, description="Whether to automatically ingest new documents"),
    session: AsyncSession = Depends(get_db_session)
):
    """Triggers an immediate poll cycle for a continuous topic subscription."""
    res = await continuous_manager.poll_subscription(
        config_id=config_id,
        engine=engine,
        session=session,
        auto_ingest=auto_ingest
    )
    if res.get("status") == "skipped":
        raise HTTPException(status_code=404, detail=res.get("reason"))
    return res
