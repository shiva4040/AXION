from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, EntityCategory, RelationType, ProvenancePointer

class ApplicabilityVerdict(str, Enum):
    """
    Mandatory verdict issued by the Applicability Guard for any transferred candidate knowledge.
    """
    ACCEPTED = "ACCEPTED"                                 # Passes structural, dimensional, physical, and consistency checks
    REJECTED = "REJECTED"                                 # Violates dimensions, core physical assumptions, or empirical evidence
    CONDITIONAL = "CONDITIONAL"                           # Holds only under explicit domain-narrowing conditions or assumptions
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION" # Missing critical variables, dimensions, or boundary parameters

class AlignmentMethod(str, Enum):
    """
    Structural alignment algorithms supported by Component 6.
    """
    STRUCTURE_MAPPING = "STRUCTURE_MAPPING"   # Gentner Structure Mapping Theory (SMT): relational isomorphism + systematicity
    GRAPH_SIGNATURE = "GRAPH_SIGNATURE"       # Graph signature / degree sequence matching
    SEMANTIC_EMBEDDING = "SEMANTIC_EMBEDDING" # Concept semantic similarity / embedding matching

class PhysicalAssumption(str, Enum):
    """Core domain assumptions commonly governing physical and scientific laws."""
    LINEARITY = "linearity"
    CONTINUUM_HYPOTHESIS = "continuum_hypothesis"
    ENERGY_CONSERVATION = "energy_conservation"
    MASS_CONSERVATION = "mass_conservation"
    MOMENTUM_CONSERVATION = "momentum_conservation"
    STEADY_STATE = "steady_state"
    ISOTROPIC = "isotropic"
    NEWTONIAN_FLUID = "newtonian_fluid"
    IDEAL_GAS = "ideal_gas"
    OHMIC_CONDUCTION = "ohmic_conduction"
    REVERSIBILITY = "reversibility"
    NON_RELATIVISTIC = "non_relativistic"
    LOCAL_THERMODYNAMIC_EQUILIBRIUM = "local_thermodynamic_equilibrium"
    LAMINAR_FLOW = "laminar_flow"

class BoundaryConstraint(BaseModel):
    """Operating boundary limits for domain parameters."""
    variable_name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None

class DomainConcept(BaseModel):
    """Entity representation within a specific domain namespace."""
    name: str
    domain: str
    category: EntityCategory = Field(default=EntityCategory.CONCEPT)
    symbol: Optional[str] = None
    si_dimension: Optional[str] = None
    role: Optional[str] = Field(
        default=None,
        description="Functional role, e.g. potential, flux, resistance, capacitance, driver, dissipator"
    )
    attributes: Dict[str, Any] = Field(default_factory=dict)
    provenance: Optional[ProvenancePointer] = None

class DomainRelation(BaseModel):
    """Relational constraint or governing law within a domain."""
    source_concept: str
    target_concept: str
    relation_type: RelationType = Field(default=RelationType.GOVERNED_BY)
    equation: Optional[str] = Field(default=None, description="Mathematical equation expressing the relation")
    epistemic_tier: EpistemicTier = Field(default=EpistemicTier.FACT_DOCUMENTED)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_snippet: Optional[str] = None
    provenance: Optional[ProvenancePointer] = None
    assumptions_required: List[str] = Field(default_factory=list)

class DomainKnowledgeBundle(BaseModel):
    """Structured knowledge payload representing an isolated scientific domain."""
    domain_name: str
    description: str = ""
    concepts: List[DomainConcept] = Field(default_factory=list)
    relations: List[DomainRelation] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    boundary_conditions: List[BoundaryConstraint] = Field(default_factory=list)

class ConceptMapping(BaseModel):
    """Analogical correspondence between a source concept and a target concept."""
    source_concept: str
    target_concept: str
    confidence: float = Field(ge=0.0, le=1.0)
    role: str
    explanation: str

class RelationMapping(BaseModel):
    """Relational alignment across domains."""
    source_relation: DomainRelation
    target_relation: Optional[DomainRelation] = None
    confidence: float = Field(ge=0.0, le=1.0)
    status: str = Field(description="'ALIGNED' (exists in both), 'PROJECTED_CANDIDATE' (source only), 'MISMATCHED'")
    explanation: str

class StructuralAlignmentResult(BaseModel):
    """Complete structural alignment between two scientific domains."""
    source_domain: str
    target_domain: str
    method: AlignmentMethod
    concept_mappings: List[ConceptMapping] = Field(default_factory=list)
    relation_mappings: List[RelationMapping] = Field(default_factory=list)
    structural_similarity_score: float = Field(ge=0.0, le=1.0)
    systematicity_score: float = Field(ge=0.0, le=1.0, description="Score reflecting preservation of higher-order relational systems")
    domain_differences: List[str] = Field(default_factory=list)
    alignable_roles: List[str] = Field(default_factory=list)

class CandidateTransfer(BaseModel):
    """A projected scientific conjecture transferred from source to target domain."""
    transfer_id: str
    source_domain: str
    target_domain: str
    source_relation: DomainRelation
    proposed_source_concept: str
    proposed_target_concept: str
    proposed_relation_type: RelationType
    proposed_equation: Optional[str] = None
    mapped_concept_names: Dict[str, str] = Field(default_factory=dict)
    mapped_symbols: Dict[str, str] = Field(default_factory=dict)
    epistemic_tier: EpistemicTier = Field(default=EpistemicTier.HYPOTHESIS_CONJECTURED)
    rationale: str
    provenance: Optional[ProvenancePointer] = None

class ApplicabilityCheckStage(BaseModel):
    """Detailed audit log for an individual verification stage."""
    stage_name: str
    passed: bool
    details: str
    diagnostics: Dict[str, Any] = Field(default_factory=dict)

class ApplicabilityEvaluation(BaseModel):
    """Comprehensive evaluation record generated by the Applicability Guard."""
    transfer_id: str
    verdict: ApplicabilityVerdict
    confidence: float = Field(ge=0.0, le=1.0)
    passed_stages: List[str] = Field(default_factory=list)
    failed_stages: List[str] = Field(default_factory=list)
    stage_results: List[ApplicabilityCheckStage] = Field(default_factory=list)
    conditions_required: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    rationale: str

class HarmonizedVariable(BaseModel):
    """Variable whose notation and units have been reconciled across domains."""
    source_symbol: str
    canonical_name: str
    domain_origins: List[str]
    si_dimension: Optional[str] = None
    resolved_symbol: str

class ComposedSystem(BaseModel):
    """Structured representation of composed multi-domain knowledge."""
    composition_id: str
    domains: List[str]
    harmonized_variables: List[HarmonizedVariable] = Field(default_factory=list)
    composed_equations: List[str] = Field(default_factory=list)
    composed_relations: List[DomainRelation] = Field(default_factory=list)
    active_assumptions: List[str] = Field(default_factory=list)
    active_constraints: List[BoundaryConstraint] = Field(default_factory=list)
    provenance_chain: List[ProvenancePointer] = Field(default_factory=list)

class TransferRecord(BaseModel):
    """End-to-end audit record for a knowledge composition and transfer operation."""
    record_id: str
    source_domain: str
    target_domain: str
    alignment: StructuralAlignmentResult
    candidate_transfers: List[CandidateTransfer] = Field(default_factory=list)
    evaluations: List[ApplicabilityEvaluation] = Field(default_factory=list)
    accepted_transfers: List[CandidateTransfer] = Field(default_factory=list)
    conditional_transfers: List[CandidateTransfer] = Field(default_factory=list)
    rejected_transfers: List[CandidateTransfer] = Field(default_factory=list)
    composed_system: Optional[ComposedSystem] = None
