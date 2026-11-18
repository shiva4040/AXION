from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, ProvenancePointer

class KnowledgeStatus(str, Enum):
    """
    Explicit status of a finding in the Validated Knowledge Memory.
    """
    VALID = "VALID"                 # Active, experimentally supported finding
    INVALIDATED = "INVALIDATED"     # Formally retracted or invalidated due to contradiction/counterevidence
    SUPERSEDED = "SUPERSEDED"       # Replaced by a higher-precision or broader finding

class ValidatedFinding(BaseModel):
    """
    Component 9 Core Entity:
    A scientifically validated finding (Epistemic Tier 4: FINDING_VALIDATED)
    holding immutable provenance, experimental support, and dependency links.
    """
    finding_id: str
    version: int = Field(default=1, ge=1)
    title: str
    statement: str
    status: KnowledgeStatus = Field(default=KnowledgeStatus.VALID)
    hypothesis_id: str
    epistemic_tier: EpistemicTier = Field(
        default=EpistemicTier.FINDING_VALIDATED,
        description="Tier 4: Empirically validated via sandbox/experimental testing"
    )
    supporting_experiment_ids: List[str] = Field(
        default_factory=list,
        description="IDs of ExperimentRecord objects that empirically confirmed this finding"
    )
    source_provenance: List[ProvenancePointer] = Field(default_factory=list)
    active_assumptions: List[str] = Field(default_factory=list)
    applicable_conditions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    derived_from_finding_ids: List[str] = Field(
        default_factory=list,
        description="IDs of prerequisite findings this finding depends upon"
    )
    superseded_by_id: Optional[str] = Field(
        default=None,
        description="ID of newer finding that supersedes this finding if status == SUPERSEDED"
    )
    invalidation_reason: Optional[str] = Field(default=None)
    created_at: str
    updated_at: str

class FindingVersionRecord(BaseModel):
    """Immutable audit trail entry recording a state change in a finding."""
    record_id: str
    finding_id: str
    version: int
    previous_status: Optional[KnowledgeStatus] = None
    new_status: KnowledgeStatus
    change_type: str # "CREATED", "INVALIDATED", "SUPERSEDED", "CORRECTED"
    reason: str
    timestamp: str

class DependentImpactReport(BaseModel):
    """Report detailing downstream findings impacted by an invalidation or supersession."""
    trigger_finding_id: str
    trigger_status: KnowledgeStatus
    directly_affected_finding_ids: List[str] = Field(default_factory=list)
    transitively_affected_finding_ids: List[str] = Field(default_factory=list)
    total_affected_count: int = 0
    recommended_action: str = "Flag affected dependent findings for re-evaluation and rerun experiments."
