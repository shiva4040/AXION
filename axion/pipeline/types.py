import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Re-export core types for seamless cross-module interoperability
from axion.core.types import (
    BoundingBox,
    EpistemicTier,
    ProvenancePointer,
    TrustTier,
)


class QuestionIntent(str, Enum):
    """Classified research goal or inquiry intent."""
    EXPLANATION = "EXPLANATION"
    QUANTITATIVE_CALCULATION = "QUANTITATIVE_CALCULATION"
    ANALOGICAL_TRANSFER = "ANALOGICAL_TRANSFER"
    HYPOTHESIS_EVALUATION = "HYPOTHESIS_EVALUATION"
    FEASIBILITY_CHECK = "FEASIBILITY_CHECK"


class VerificationVerdict(str, Enum):
    """Independent verification gatekeeper verdicts."""
    VERIFIED = "VERIFIED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    ABSTAIN_INSUFFICIENT_EVIDENCE = "ABSTAIN_INSUFFICIENT_EVIDENCE"
    ABSTAIN_CONTRADICTORY_EVIDENCE = "ABSTAIN_CONTRADICTORY_EVIDENCE"
    INVALID_REASONING = "INVALID_REASONING"
    INVALID_PROVENANCE = "INVALID_PROVENANCE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


class QuestionSpec(BaseModel):
    """
    Stage 01 Data Model:
    Structured specification resulting from question processing and domain classification.
    """
    query_id: str = Field(default_factory=lambda: f"q-{uuid.uuid4().hex[:8]}")
    raw_query: str
    intent: QuestionIntent = Field(default=QuestionIntent.EXPLANATION)
    target_variables: List[str] = Field(default_factory=list)
    domain_tags: List[str] = Field(default_factory=list)
    identified_constraints: Dict[str, Any] = Field(default_factory=dict)
    extracted_concepts: List[str] = Field(default_factory=list)
    declared_parameters: Dict[str, Any] = Field(default_factory=dict)
    document_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AcquiredChunk(BaseModel):
    """Atomic acquired text passage with positional provenance."""
    chunk_id: str
    document_id: str
    page_number: int
    text_content: str
    similarity_score: float = 0.0
    source_title: Optional[str] = None
    source_uri: Optional[str] = None
    provenance: ProvenancePointer
    bounding_box: Optional[BoundingBox] = None


class AcquisitionPayload(BaseModel):
    """
    Stage 02 Data Model:
    Aggregated evidence payload containing retrieved document chunks and candidate memory items.
    """
    query_id: str
    retrieved_chunks: List[AcquiredChunk] = Field(default_factory=list)
    candidate_memory_items: List[Dict[str, Any]] = Field(default_factory=list)
    sources_queried: List[str] = Field(default_factory=list)
    total_retrieved: int = 0
    acquisition_latency_ms: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedClaim(BaseModel):
    """
    Stage 03 Data Model:
    Atomic factual assertion or equation extracted from acquired literature with strict provenance.
    """
    claim_id: str = Field(default_factory=lambda: f"clm-{uuid.uuid4().hex[:8]}")
    statement: str
    epistemic_tier: EpistemicTier = Field(default=EpistemicTier.FACT_DOCUMENTED)
    conditions: List[str] = Field(
        default_factory=list,
        description="Operational qualifiers, e.g. 'T > 300K', 'laminar flow'"
    )
    equations: List[str] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list)
    provenance: ProvenancePointer
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ComposedSystem(BaseModel):
    """
    Stage 04 Data Model:
    Harmonized multi-document or cross-domain model ready for formal reasoning.
    """
    system_id: str = Field(default_factory=lambda: f"sys-{uuid.uuid4().hex[:8]}")
    unified_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Canonical variable mapping to physical dimensions or symbols"
    )
    active_assumptions: List[str] = Field(default_factory=list)
    coupled_equations: List[str] = Field(default_factory=list)
    claims: List[ExtractedClaim] = Field(default_factory=list)
    boundary_limits: Dict[str, Any] = Field(default_factory=dict)
    participating_domains: List[str] = Field(default_factory=list)


class ReasoningTrace(BaseModel):
    """
    Stage 05 Data Model:
    Step-by-step mathematical substitution, derivations, and causal proof DAG.
    """
    trace_id: str = Field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:8]}")
    steps: List[str] = Field(default_factory=list)
    calculated_values: Dict[str, Any] = Field(default_factory=dict)
    inferred_premises: List[str] = Field(default_factory=list)
    dependency_dag: Optional[Dict[str, List[str]]] = None
    execution_error: Optional[str] = None


class VerificationAuditReport(BaseModel):
    """
    Stage 06 Data Model:
    Verification report assessing quotation validity, contradictions, and boundary guardrails.
    """
    report_id: str = Field(default_factory=lambda: f"aud-{uuid.uuid4().hex[:8]}")
    verdict: str = Field(default="VERIFIED", description="VERIFIED, REJECTED, or ABSTAIN")
    abstention_reason: Optional[str] = None
    quotation_checks_passed: bool = True
    contradiction_detected: bool = False
    applicability_checks_passed: bool = True
    audit_details: Dict[str, Any] = Field(default_factory=dict)


class SupportingEvidenceItem(BaseModel):
    """Citation item backing a final answer claim."""
    claim: str
    citation: str
    verbatim_quote: str
    provenance: Optional[ProvenancePointer] = None


class StageExecutionLog(BaseModel):
    """Structured telemetry record for a single pipeline stage execution."""
    stage_number: int
    stage_name: str
    status: str = "SUCCESS"  # SUCCESS, FAILED, SKIPPED, TIMEOUT
    started_at: str
    duration_ms: float
    summary: Optional[str] = None
    error_message: Optional[str] = None


class PipelineAnswerResponse(BaseModel):
    """
    Stage 08 Data Model:
    Structured, fully attributed pipeline response or explicit abstention notice.
    """
    query_id: str
    query: str
    verdict: str = Field(default="ANSWERABLE")
    direct_answer: str
    supporting_evidence: List[SupportingEvidenceItem] = Field(default_factory=list)
    active_assumptions: List[str] = Field(default_factory=list)
    calculation_steps: List[str] = Field(default_factory=list)
    is_abstained: bool = False
    abstention_reason: Optional[str] = None
    execution_logs: List[StageExecutionLog] = Field(default_factory=list)
    total_latency_ms: float = 0.0
