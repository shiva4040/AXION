from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from axion.core.types import EpistemicTier, ProvenancePointer
from axion.transfer.types import ApplicabilityVerdict

class ExperimentType(str, Enum):
    SYMBOLIC_DERIVATION = "SYMBOLIC_DERIVATION"
    NUMERICAL_SIMULATION = "NUMERICAL_SIMULATION"
    LABORATORY_MEASUREMENT = "LABORATORY_MEASUREMENT"

class ExperimentProposal(BaseModel):
    """Concrete validation procedure proposed to test or falsify a hypothesis."""
    proposal_id: str
    experiment_type: ExperimentType
    description: str
    target_variables: List[str] = Field(default_factory=list)
    expected_signature: str = Field(description="Observable signature expected if hypothesis holds")
    falsification_threshold: str = Field(description="Quantitative or qualitative threshold indicating rejection")

class StructuredHypothesis(BaseModel):
    """
    Component 7 Output:
    A formal scientific hypothesis generated from composed cross-domain knowledge
    and accepted/conditional analogical transfers.
    Strictly demarcated under Epistemic Tier 3 (HYPOTHESIS_CONJECTURED).
    """
    hypothesis_id: str
    title: str
    premise: List[str] = Field(description="Grounding empirical facts and relations")
    mechanism: str = Field(description="Detailed cross-domain causal mechanism")
    prediction: str = Field(description="Falsifiable, testable empirical prediction")
    counterevidence_conditions: List[str] = Field(
        description="Explicit observations that would falsify the hypothesis"
    )
    suggested_experiments: List[ExperimentProposal] = Field(default_factory=list)
    uncertainty_level: float = Field(ge=0.0, le=1.0, description="Uncertainty score (0.0 = high confidence conjecture, 1.0 = highly uncertain)")
    epistemic_tier: EpistemicTier = Field(
        default=EpistemicTier.HYPOTHESIS_CONJECTURED,
        description="Strictly Demarcated: Must NEVER be stored or presented as FACT_DOCUMENTED"
    )
    source_domains: List[str] = Field(default_factory=list)
    target_domain: str
    applicability_verdict: ApplicabilityVerdict
    required_conditions: List[str] = Field(default_factory=list)
    provenance_links: List[ProvenancePointer] = Field(default_factory=list)
    epistemic_disclaimer: str = (
        "EPISTEMIC DEMARCATION: This statement is a generated scientific hypothesis (Tier 3 Conjecture) "
        "derived via cross-domain analogical projection. It has NOT been validated through empirical laboratory "
        "experimentation or certified containerized sandbox execution."
    )
