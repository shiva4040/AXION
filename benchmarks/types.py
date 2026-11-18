from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.transfer.types import DomainKnowledgeBundle, ApplicabilityVerdict

class ProblemTier(str, Enum):
    TIER_E = "TIER_E"  # Easy: Single-domain factual/relational reasoning
    TIER_I = "TIER_I"  # Intermediate: Multi-domain knowledge composition
    TIER_D = "TIER_D"  # Difficult: Cross-domain analogical transfer (includes negative test cases)

class BenchmarkProblem(BaseModel):
    """A scientific benchmark evaluation problem."""
    problem_id: str
    tier: ProblemTier
    title: str
    query: str
    domains: List[DomainKnowledgeBundle]
    source_domain_name: Optional[str] = None
    target_domain_name: Optional[str] = None
    ground_truth_answer: str
    expected_verdict: Optional[ApplicabilityVerdict] = None  # Expected verdict if Tier D
    is_negative_case: bool = False                          # If True, the proposed analogy violates domain physics and MUST be rejected
    expected_falsification_conditions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class SystemCondition(str, Enum):
    BASELINE_RAG = "BASELINE_RAG"                   # Condition 1: Conventional RAG
    KG_REASONING_ONLY = "KG_REASONING_ONLY"         # Condition 2: KG reasoning without cross-domain transfer
    AXION_FULL_ENGINE = "AXION_FULL_ENGINE"         # Condition 3: Full AXION (SMT + Composition + ASP + Guard + Generator)
    AXION_ABLATION_SIGNATURE = "AXION_ABLATION_SIGNATURE" # Condition 4: Graph signature ablation without SMT systematicity

class ProblemEvaluationResult(BaseModel):
    problem_id: str
    tier: ProblemTier
    condition: SystemCondition
    is_success: bool
    verdict: Optional[str] = None
    expected_verdict: Optional[str] = None
    correct_guard_decision: Optional[bool] = None
    false_acceptance: bool = False
    false_rejection: bool = False
    reasoning_summary: str
    execution_time_ms: float

class BenchmarkSummaryReport(BaseModel):
    total_problems: int
    tier_counts: Dict[str, int]
    condition_results: Dict[str, Dict[str, Any]]
    false_acceptance_rates: Dict[str, float]
    false_rejection_rates: Dict[str, float]
    overall_accuracy_by_condition: Dict[str, float]
    tier_accuracy_breakdown: Dict[str, Dict[str, float]]
