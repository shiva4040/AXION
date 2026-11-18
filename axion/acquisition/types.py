import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, TrustTier, ProvenancePointer

def get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class DocumentType(str, Enum):
    """Classification of acquired scientific content."""
    PAPER = "paper"
    ABSTRACT = "abstract"
    DATASET = "dataset"
    WEB_PAGE = "web_page"
    TECHNICAL_REPORT = "technical_report"
    DOCUMENT = "document"

class AccessStatus(str, Enum):
    """Legal and technical access status of acquired content."""
    OPEN_ACCESS = "open_access"
    RESTRICTED = "restricted"
    ABSTRACT_ONLY = "abstract_only"
    METADATA_ONLY = "metadata_only"
    SUBSCRIPTION = "subscription"

class AcquisitionMode(str, Enum):
    """Operational mode of the acquisition engine."""
    ON_DEMAND = "on_demand"
    CONTINUOUS = "continuous"

class SourceDocument(BaseModel):
    """
    Unified common data model for all acquired information sources.
    Every connector must normalize external records into this structure.
    """
    id: str = Field(default_factory=lambda: f"src-{uuid.uuid4().hex[:12]}")
    title: str
    content: str
    authors: List[str] = Field(default_factory=list)
    source_name: str
    source_url: Optional[str] = None
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    document_type: DocumentType = DocumentType.ABSTRACT
    license: Optional[str] = "Unknown"
    access_status: AccessStatus = AccessStatus.ABSTRACT_ONLY
    retrieval_date: str = Field(default_factory=get_utc_now_iso)
    is_full_text: bool = False
    relevance_score: float = 0.0
    epistemic_tier: EpistemicTier = EpistemicTier.FACT_DOCUMENTED
    trust_tier: TrustTier = TrustTier.PEER_REVIEWED
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Optional[ProvenancePointer] = None

class SearchRequest(BaseModel):
    """User-facing or pipeline-facing external search request."""
    query: str
    sources: Optional[List[str]] = None
    max_results_per_source: int = Field(default=5, ge=1, le=50)
    min_relevance: float = Field(default=0.1, ge=0.0, le=1.0)
    mode: AcquisitionMode = AcquisitionMode.ON_DEMAND

class SearchResponse(BaseModel):
    """Response containing discovered, deduplicated, and ranked documents."""
    query: str
    identified_terms: List[str] = Field(default_factory=list)
    sources_queried: List[str] = Field(default_factory=list)
    total_discovered: int = 0
    total_deduplicated: int = 0
    documents: List[SourceDocument] = Field(default_factory=list)
    execution_time_ms: float = 0.0

class IngestAcquiredRequest(BaseModel):
    """Request to ingest selected acquired documents into AXION memory & vector store."""
    documents: Optional[List[SourceDocument]] = None
    document_ids: Optional[List[str]] = None
    extract_knowledge_graph: bool = True

class IngestAcquiredResponse(BaseModel):
    """Summary of ingested documents, chunks, and knowledge graph extractions."""
    ingested_count: int = 0
    document_ids: List[str] = Field(default_factory=list)
    total_chunks_created: int = 0
    graph_entities_created: int = 0
    graph_relations_created: int = 0
    errors: List[str] = Field(default_factory=list)

class SourceHealthStatus(BaseModel):
    """Health, connectivity, and licensing status of a source connector."""
    source_name: str
    source_type: str
    is_available: bool
    status_message: str
    requires_auth: bool = False
    is_authenticated: bool = False
    rate_limit_info: Optional[str] = None
    supported_doc_types: List[DocumentType] = Field(default_factory=list)

class ContinuousSourceConfig(BaseModel):
    """Configuration for standing periodic discovery topics."""
    config_id: str = Field(default_factory=lambda: f"cfg-{uuid.uuid4().hex[:8]}")
    source_name: str
    search_query: str
    poll_interval_seconds: int = 3600
    enabled: bool = True
    last_poll_timestamp: Optional[str] = None
    seen_identifiers: List[str] = Field(default_factory=list)
