import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from axion.database.connection import Base
from axion.core.types import EpistemicTier, TrustTier, EntityCategory, RelationType

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Document(Base):
    """Core document metadata registry."""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(512), nullable=False)
    source_type = Column(String(32), nullable=False, default="pdf") # 'pdf', 'web_url', 'api', 'dataset'
    source_uri = Column(Text, nullable=False)
    file_hash_sha256 = Column(String(64), unique=True, nullable=False, index=True)
    mime_type = Column(String(64), nullable=False, default="application/pdf")
    page_count = Column(Integer, nullable=False, default=1)
    trust_tier = Column(String(32), nullable=False, default=TrustTier.UNVERIFIED.value)
    license_type = Column(String(64), default="UNKNOWN")
    doc_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index")


class DocumentChunk(Base):
    """Extracted text chunk with positional provenance and vector embedding."""
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    structural_header = Column(String(255), nullable=True)
    is_equation_block = Column(Boolean, default=False)
    
    # Vector embedding stored as JSON array of floats for portability,
    # with pgvector type support when connected to PostgreSQL.
    embedding = Column(JSON, nullable=True)
    embedding_model = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    bounding_boxes = relationship("DocumentBoundingBox", back_populates="chunk", cascade="all, delete-orphan")
    provenance_records = relationship("EdgeProvenance", back_populates="chunk")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_idx"),
    )


class DocumentBoundingBox(Base):
    """Bounding box coordinates on a specific page for visual citation highlighting."""
    __tablename__ = "document_bounding_boxes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    x0 = Column(Float, nullable=False)
    y0 = Column(Float, nullable=False)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)

    # Relationship
    chunk = relationship("DocumentChunk", back_populates="bounding_boxes")


class GraphNode(Base):
    """Knowledge Graph Conceptual Entity."""
    __tablename__ = "graph_nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_name = Column(String(255), nullable=False)
    domain_namespace = Column(String(64), nullable=False, index=True) # e.g. "physics:thermo", "eng:electrical"
    category = Column(String(32), nullable=False, default=EntityCategory.CONCEPT.value, index=True)
    symbol = Column(String(32), nullable=True)
    si_dimension = Column(String(64), nullable=True) # e.g. "[M][L]2[T]-3"
    description = Column(Text, nullable=True)
    attributes = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    outgoing_edges = relationship("GraphEdge", foreign_keys="GraphEdge.source_node_id", back_populates="source_node", cascade="all, delete-orphan")
    incoming_edges = relationship("GraphEdge", foreign_keys="GraphEdge.target_node_id", back_populates="target_node", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("canonical_name", "domain_namespace", name="uq_node_name_domain"),
    )


class GraphEdge(Base):
    """Attributed Directed Scientific Relationship."""
    __tablename__ = "graph_edges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_node_id = Column(String(36), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(String(36), ForeignKey("graph_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type = Column(String(64), nullable=False, default=RelationType.GOVERNED_BY.value, index=True)
    epistemic_tier = Column(String(32), nullable=False, default=EpistemicTier.FACT_DOCUMENTED.value)
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    source_node = relationship("GraphNode", foreign_keys=[source_node_id], back_populates="outgoing_edges")
    target_node = relationship("GraphNode", foreign_keys=[target_node_id], back_populates="incoming_edges")
    provenance = relationship("EdgeProvenance", back_populates="edge", cascade="all, delete-orphan")


class EdgeProvenance(Base):
    """Links graph edges directly to primary document chunks."""
    __tablename__ = "edge_provenance"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    edge_id = Column(String(36), ForeignKey("graph_edges.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    extracted_snippet = Column(Text, nullable=False)
    extraction_method = Column(String(32), default="LLM_EXTRACTED") # 'LLM_EXTRACTED', 'RULE_EXTRACTED'
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    edge = relationship("GraphEdge", back_populates="provenance")
    chunk = relationship("DocumentChunk", back_populates="provenance_records")


class Investigation(Base):
    """Root container for a research or engineering investigation."""
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    initial_query = Column(Text, nullable=False)
    primary_domain = Column(String(64), nullable=True)
    target_domains = Column(JSON, default=list)
    status = Column(String(32), default="ACTIVE") # 'ACTIVE', 'COMPLETED', 'FAILED'
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
