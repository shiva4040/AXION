from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, RelationType

class SubProblemStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SOLVED = "SOLVED"
    BLOCKED = "BLOCKED"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"

class SubProblem(BaseModel):
    id: str
    order: int
    title: str
    description: str
    target_domain: str
    required_variables: List[str] = Field(default_factory=list)
    status: SubProblemStatus = Field(default=SubProblemStatus.PENDING)
    equations_to_evaluate: List[str] = Field(default_factory=list)
    assigned_evidence_chunk_ids: List[str] = Field(default_factory=list)

class DependencyEdge(BaseModel):
    from_subproblem_id: str
    to_subproblem_id: str
    dependency_type: str = "REQUIRES" # "REQUIRES", "INPUT_PARAMETER_FOR"

class ReasoningDAG(BaseModel):
    problem_id: str
    goal: str
    sub_problems: Dict[str, SubProblem] = Field(default_factory=dict)
    dependencies: List[DependencyEdge] = Field(default_factory=list)
    topological_order: List[str] = Field(default_factory=list)
    is_acyclic: bool = True

class ContradictionAlert(BaseModel):
    concept_a: str
    concept_b: str
    relation_1: RelationType
    source_chunk_1: str
    snippet_1: str
    relation_2: RelationType
    source_chunk_2: str
    snippet_2: str
    explanation: str

class SubProblemExecutionResult(BaseModel):
    subproblem_id: str
    title: str
    epistemic_tier: EpistemicTier
    derived_conclusions: List[str] = Field(default_factory=list)
    equations_verified: List[str] = Field(default_factory=list)
    failed_validations: List[str] = Field(default_factory=list)
    missing_variables: List[str] = Field(default_factory=list)
    assumptions_made: List[str] = Field(default_factory=list)
    supporting_citations: List[Dict[str, Any]] = Field(default_factory=list)

class ReasoningOutcome(BaseModel):
    problem_id: str
    goal: str
    dag: ReasoningDAG
    step_results: List[SubProblemExecutionResult]
    contradictions_detected: List[ContradictionAlert] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    is_fully_solved: bool
    summary_explanation: str
    epistemic_disclaimer: str = (
        "Notice: Conclusions are logically deduced and symbolically verified against available evidence. "
        "Missing premises and unverified assumptions are explicitly flagged."
    )
