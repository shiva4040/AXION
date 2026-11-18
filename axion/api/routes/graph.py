from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from axion.database.connection import get_db_session
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.knowledge_graph.extractor import KnowledgeGraphExtractor
from axion.database.models import DocumentChunk
from sqlalchemy import select

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])

class NodeSummary(BaseModel):
    id: str
    canonical_name: str
    domain: str
    category: str
    symbol: Optional[str] = None
    si_dimension: Optional[str] = None

class EdgeSummary(BaseModel):
    id: str
    source: str
    target: str
    relation_type: str
    epistemic_tier: str
    confidence: float

class SubgraphResponse(BaseModel):
    nodes: List[NodeSummary]
    edges: List[EdgeSummary]

class PathResponse(BaseModel):
    source: str
    target: str
    paths: List[List[str]]

@router.post("/extract-from-chunk/{chunk_id}")
async def extract_graph_from_chunk(
    chunk_id: str,
    domain: str = Query("general_science"),
    session: AsyncSession = Depends(get_db_session)
):
    """Triggers entity and relation extraction on a specific document chunk."""
    stmt = select(DocumentChunk).where(DocumentChunk.id == chunk_id)
    res = await session.execute(stmt)
    chunk = res.scalars().first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    extractor = KnowledgeGraphExtractor(default_domain=domain)
    extraction = await extractor.extract_from_chunk(chunk.text_content, domain=domain)

    store = KnowledgeGraphStore(session)
    stats = await store.add_extraction_result(extraction, chunk_id=chunk.id, default_domain=domain)
    return {"status": "success", "extraction": extraction.model_dump(), "stats": stats}

@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    domain: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Retrieves nodes and edges for visualization in Cytoscape."""
    store = KnowledgeGraphStore(session)
    G = await store.export_to_networkx(domain_filter=domain)
    
    nodes = [
        NodeSummary(
            id=data.get("id", name),
            canonical_name=name,
            domain=data.get("domain", "general"),
            category=data.get("category", "CONCEPT"),
            symbol=data.get("symbol"),
            si_dimension=data.get("si_dimension")
        )
        for name, data in G.nodes(data=True)
    ]
    edges = [
        EdgeSummary(
            id=data.get("id", f"{u}->{v}"),
            source=u,
            target=v,
            relation_type=data.get("relation_type", "governed_by"),
            epistemic_tier=data.get("epistemic_tier", "FACT_DOCUMENTED"),
            confidence=data.get("confidence", 1.0)
        )
        for u, v, data in G.edges(data=True)
    ]
    return SubgraphResponse(nodes=nodes, edges=edges)

@router.get("/paths", response_model=PathResponse)
async def find_paths_between_concepts(
    source: str,
    target: str,
    max_hops: int = 4,
    session: AsyncSession = Depends(get_db_session)
):
    """Discovers paths connecting two concepts across the graph."""
    store = KnowledgeGraphStore(session)
    paths = await store.find_paths(source_concept=source, target_concept=target, max_hops=max_hops)
    return PathResponse(source=source, target=target, paths=paths)
