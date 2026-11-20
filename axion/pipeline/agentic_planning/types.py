import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class AgentRole(str, Enum):
    """The 13 specialized research agent roles in AXION Stage 01."""
    RESEARCH_COORDINATOR = "coordinator"
    INTENT_UNDERSTANDING = "intent_agent"
    DOMAIN_DISCOVERY = "domain_agent"
    QUESTION_DECOMPOSITION = "decomposition_agent"
    CONCEPTS_DISCOVERY = "concepts_agent"
    VARIABLES_AND_EQUATIONS = "equations_agent"
    PROCESS_MAPPING = "process_agent"
    MATERIALS_AND_TECHNOLOGY = "materials_agent"
    EVIDENCE_REQUIREMENTS = "evidence_agent"
    CROSS_DOMAIN_CONNECTION = "cross_domain_agent"
    KNOWLEDGE_GAP_CONSTRAINT = "knowledge_gap_agent"
    CRITICAL_REVIEWER = "critical_reviewer"
    COMPLETENESS_EVALUATOR = "completeness_evaluator"

    # Convenient aliases
    COORDINATOR = "coordinator"
    VARIABLES_EQUATIONS = "equations_agent"
    MATERIALS_TECHNOLOGY = "materials_agent"
    CROSS_DOMAIN = "cross_domain_agent"
    KNOWLEDGE_GAP = "knowledge_gap_agent"


class AgentStatus(str, Enum):
    IDLE = "idle"
    INVESTIGATING = "investigating"
    COMPLETED = "completed"
    FAILED = "failed"
    CRITIQUED = "critiqued"
    REFINED = "refined"


class FindingType(str, Enum):
    INTENT = "intent"
    DOMAIN = "domain"
    SUBQUESTION = "subquestion"
    CONCEPT = "concept"
    EQUATION = "equation"
    VARIABLE = "variable"
    PHYSICAL_PROCESS = "physical_process"
    MATERIAL = "material"
    MATERIAL_TECH = "material"
    COMPONENT = "component"
    EVIDENCE_REQUIREMENT = "evidence_requirement"
    EVIDENCE_REQ = "evidence_requirement"
    CROSS_DOMAIN_BRIDGE = "cross_domain_bridge"
    CROSS_DOMAIN = "cross_domain_bridge"
    KNOWLEDGE_GAP = "knowledge_gap"
    CRITICISM = "criticism"
    CRITIQUE = "criticism"
    COMPLETENESS = "completeness"
    SYNTHESIS = "synthesis"


class AgentStatusRecord(BaseModel):
    """Execution telemetry and live status of a specialized research agent."""
    agent_id: str = Field(default_factory=lambda: f"ag-{uuid.uuid4().hex[:6]}")
    role: AgentRole
    display_name: str = ""
    name: str = ""
    responsibility: str = ""
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    latency_ms: float = 0.0
    findings_count: int = 0
    criticisms_count: int = 0
    error_message: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.name and self.display_name:
            self.name = self.display_name
        elif not self.display_name and self.name:
            self.display_name = self.name


class AgentFinding(BaseModel):
    """Atomic structured research discovery produced by an agent."""
    id: str = Field(default_factory=lambda: f"fnd-{uuid.uuid4().hex[:8]}")
    agent_role: AgentRole
    finding_type: FindingType
    title: str
    content: str
    scientific_justification: str = ""
    related_subquestions: List[str] = Field(default_factory=list)
    related_domains: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    uncertainty_notes: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"  # active, refined, challenged, superseded


class IntentAnalysis(BaseModel):
    """Agent 2: Deep intent and research goal specification."""
    original_question: str
    interpreted_objective: str
    expected_outcome: str
    problem_type: str = "conceptual_explanation"
    explicit_requirements: List[str] = Field(default_factory=list)
    inferred_requirements: List[str] = Field(default_factory=list)
    ambiguities: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    clarification_prompt: Optional[str] = None
    confidence: float = 0.95
    justification: str = ""


class DiscoveredDomain(BaseModel):
    """Agent 3: Scientific domain discovery record with physical justification."""
    domain_name: str
    tier: str = "primary"  # primary, secondary, supporting, conditional
    scientific_rationale: str
    physical_process_explained: str
    supported_subquestions: List[str] = Field(default_factory=list)
    contributed_concepts: List[str] = Field(default_factory=list)


class HierarchicalSubQuestion(BaseModel):
    """Agent 4: Hierarchical research subquestion specification."""
    id: str  # e.g. SQ-1, SQ-1.1, SQ-2
    level: str = "subquestion"  # main, major_area, subquestion, investigative
    question: str
    purpose: str = ""
    target_domain: Optional[str] = None
    information_needed: List[str] = Field(default_factory=list)
    relevant_domains: List[str] = Field(default_factory=list)
    required_concepts: List[str] = Field(default_factory=list)
    required_variables: List[str] = Field(default_factory=list)
    expected_evidence: str = ""
    depends_on: List[str] = Field(default_factory=list)
    priority: str = "HIGH"  # HIGH, MEDIUM, LOW
    completion_criteria: str = ""
    status: str = "pending"


class ScientificConcept(BaseModel):
    """Agent 5: Fundamental scientific concept, law, or mechanism."""
    id: str = Field(default_factory=lambda: f"cpt-{uuid.uuid4().hex[:8]}")
    name: str
    category: str = "principle"  # principle, law, mechanism, definition, model, constitutive_relation
    definition: str
    scientific_explanation: str
    mathematical_formulation: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    related_subquestions: List[str] = Field(default_factory=list)
    related_domains: List[str] = Field(default_factory=list)
    discovering_agent: str = "concepts_agent"


class GoverningEquation(BaseModel):
    """Agent 6: Mathematical formulation with symbol definitions and validity boundaries."""
    id: str = Field(default_factory=lambda: f"eq-{uuid.uuid4().hex[:8]}")
    name: str = "Governing Equation"
    equation_latex: str = ""
    latex: str = ""
    lhs: str = ""
    rhs: str = ""
    symbols: Dict[str, str] = Field(default_factory=dict)
    symbol_definitions: Dict[str, str] = Field(default_factory=dict)
    si_units: Dict[str, str] = Field(default_factory=dict)
    applicable_conditions: List[str] = Field(default_factory=list)
    validity_boundaries: str = "Standard physical regime"
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    rationale: str = ""
    required_inputs: List[str] = Field(default_factory=list)
    related_subquestions: List[str] = Field(default_factory=list)
    is_established: bool = True  # True if standard physics, False if proposed/conjectured
    discovering_agent: str = "equations_agent"

    def model_post_init(self, __context: Any) -> None:
        if not self.equation_latex and self.latex:
            self.equation_latex = self.latex
        elif not self.latex and self.equation_latex:
            self.latex = self.equation_latex
        if not self.symbol_definitions and self.symbols:
            self.symbol_definitions = self.symbols
        elif not self.symbols and self.symbol_definitions:
            self.symbols = self.symbol_definitions


class PhysicalProcessStep(BaseModel):
    """Agent 7: Step in the physical or logical process chain."""
    step_number: int = 1
    process_name: str = ""
    name: str = ""
    input_state: str = ""
    output_state: str = ""
    physical_mechanism: str = ""
    mechanism: str = ""
    governing_principle: str = ""
    governing_laws: List[str] = Field(default_factory=list)
    critical_factors: List[str] = Field(default_factory=list)
    required_components_materials: List[str] = Field(default_factory=list)
    variables_involved: List[str] = Field(default_factory=list)
    energy_losses: str = "None"
    dependencies: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.process_name and self.name:
            self.process_name = self.name
        elif not self.name and self.process_name:
            self.name = self.process_name
        if not self.physical_mechanism and self.mechanism:
            self.physical_mechanism = self.mechanism
        elif not self.mechanism and self.physical_mechanism:
            self.mechanism = self.physical_mechanism


class MaterialOrComponent(BaseModel):
    """Agent 8: Specific material, device, or component specification."""
    id: str = Field(default_factory=lambda: f"mat-{uuid.uuid4().hex[:8]}")
    name: str = "Material"
    category: str = "material"
    specifications: str = ""
    function: str = ""
    role: str = ""
    operating_limits: str = "Standard conditions"
    operating_ranges: str = "Standard conditions"
    material_properties: Dict[str, str] = Field(default_factory=dict)
    performance_parameters: Dict[str, str] = Field(default_factory=dict)
    advantages: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    practical_constraints: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    evaluation_evidence_needed: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.function and self.role:
            self.function = self.role
        elif not self.role and self.function:
            self.role = self.function


class EvidenceRequirement(BaseModel):
    """Agent 9: Explicit knowledge requirement for Stage 02 acquisition."""
    id: str = Field(default_factory=lambda: f"req-{uuid.uuid4().hex[:8]}")
    requirement_id: str = ""
    description: str = ""
    information_needed: str = ""
    subquestion_id: str = ""
    target_subquestion: str = ""
    involved_domains: List[str] = Field(default_factory=list)
    target_sources: List[str] = Field(default_factory=list)
    expected_source_types: List[str] = Field(default_factory=lambda: ["paper", "technical_doc"])
    recommended_queries: List[str] = Field(default_factory=list)
    required_parameters: List[str] = Field(default_factory=list)
    required_data_points: List[str] = Field(default_factory=list)
    quality_criteria: str = "Peer-reviewed literature or calibrated empirical data"
    verification_criteria: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.requirement_id and self.id:
            self.requirement_id = self.id
        elif not self.id and self.requirement_id:
            self.id = self.requirement_id
        if not self.description and self.information_needed:
            self.description = self.information_needed
        elif not self.information_needed and self.description:
            self.information_needed = self.description
        if not self.subquestion_id and self.target_subquestion:
            self.subquestion_id = self.target_subquestion
        elif not self.target_subquestion and self.subquestion_id:
            self.target_subquestion = self.subquestion_id
        if not self.verification_criteria and self.quality_criteria:
            self.verification_criteria = self.quality_criteria
        elif not self.quality_criteria and self.verification_criteria:
            self.quality_criteria = self.verification_criteria


class CrossDomainBridgeProposal(BaseModel):
    """Agent 10: Interdisciplinary connection proposal with physical justification."""
    id: str = Field(default_factory=lambda: f"brg-{uuid.uuid4().hex[:8]}")
    source_domain: str = ""
    target_domain: str = ""
    source_concept: str = ""
    target_concept: str = ""
    shared_principle: str = ""
    analogical_mapping: str = ""
    scientific_justification: str = ""
    mathematical_correspondence: str = ""
    mathematical_compatibility: str = ""
    validity_limits: str = "Standard conditions"
    research_value: str = ""
    validity_conditions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    verification_evidence_needed: str = ""
    reviewer_verdict: str = "ACCEPTED"  # ACCEPTED, CONDITIONAL, REJECTED
    discovering_agent: str = "cross_domain_agent"

    def model_post_init(self, __context: Any) -> None:
        if not self.mathematical_correspondence and self.mathematical_compatibility:
            self.mathematical_correspondence = self.mathematical_compatibility
        elif not self.mathematical_compatibility and self.mathematical_correspondence:
            self.mathematical_compatibility = self.mathematical_correspondence
        if not self.scientific_justification and self.analogical_mapping:
            self.scientific_justification = self.analogical_mapping
        elif not self.analogical_mapping and self.scientific_justification:
            self.analogical_mapping = self.scientific_justification


class KnowledgeGap(BaseModel):
    """Agent 11: Missing variable, unverified assumption, or operational limitation."""
    id: str = Field(default_factory=lambda: f"gap-{uuid.uuid4().hex[:8]}")
    gap_id: str = ""
    gap_description: str = ""
    description: str = ""
    gap_type: str = "missing_parameter"  # missing_parameter, unverified_assumption, practical_limitation, boundary_uncertainty
    severity: str = "MEDIUM"
    impact_on_research: str = ""
    resolution_approach: str = ""
    affected_subquestion_ids: List[str] = Field(default_factory=list)
    recommended_stage02_search: str = ""
    recommended_stage02_searches: List[str] = Field(default_factory=list)
    discovering_agent: str = "knowledge_gap_agent"
    is_resolved: bool = False

    def model_post_init(self, __context: Any) -> None:
        if not self.gap_id and self.id:
            self.gap_id = self.id
        elif not self.id and self.gap_id:
            self.id = self.gap_id
        if not self.gap_description and self.description:
            self.gap_description = self.description
        elif not self.description and self.gap_description:
            self.description = self.gap_description


class AgentCriticism(BaseModel):
    """Agent 12: Independent critical challenge / critique from Critical Reviewer."""
    id: str = Field(default_factory=lambda: f"crt-{uuid.uuid4().hex[:8]}")
    criticism_id: str = ""
    reviewer_agent: AgentRole = AgentRole.CRITICAL_REVIEWER
    target_agent: Union[AgentRole, str] = AgentRole.VARIABLES_AND_EQUATIONS
    target_item: str = ""
    target_finding_id: Optional[str] = None
    issue_identified: str = ""
    criticism_type: str = ""
    scientific_reason: str = ""
    rationale: str = ""
    severity: str = "MODERATE"  # CRITICAL, MODERATE, SUGGESTION
    suggested_correction: str = ""
    proposed_correction: str = ""
    reinvestigation_required: bool = False
    resolved: bool = False
    status: str = "RESOLVED_IN_PLAN"
    resolution_notes: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.criticism_id and self.id:
            self.criticism_id = self.id
        elif not self.id and self.criticism_id:
            self.id = self.criticism_id
        if not self.scientific_reason and self.rationale:
            self.scientific_reason = self.rationale
        elif not self.rationale and self.scientific_reason:
            self.rationale = self.scientific_reason
        if not self.suggested_correction and self.proposed_correction:
            self.suggested_correction = self.proposed_correction
        elif not self.proposed_correction and self.suggested_correction:
            self.proposed_correction = self.suggested_correction


class ReviewEvent(BaseModel):
    """Structured review discussion record between agents."""
    id: str = Field(default_factory=lambda: f"rev-{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = "review"  # critique, refinement, resolution, disagreement
    review_round: int = 1
    criticisms_raised: int = 0
    agent_role: AgentRole = AgentRole.CRITICAL_REVIEWER
    message: str = ""
    review_summary: str = ""
    critical_issues: List[str] = Field(default_factory=list)
    resolved_modifications: List[str] = Field(default_factory=list)
    unresolved_disagreements: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.message and self.review_summary:
            self.message = self.review_summary
        elif not self.review_summary and self.message:
            self.review_summary = self.message


class CompletenessEvaluation(BaseModel):
    """Agent 13: Systematic completeness audit and readiness verdict."""
    intent_coverage_score: float = 0.95
    domain_coverage_score: float = 0.95
    subquestion_coverage_score: float = 0.95
    equation_coverage_score: float = 0.90
    evidence_coverage_score: float = 0.90
    overall_completeness: float = 0.93
    overall_score: float = 0.93
    intent_score: float = 0.95
    domain_score: float = 0.95
    subquestion_score: float = 0.95
    equation_score: float = 0.90
    evidence_score: float = 0.90
    completed_requirements: List[str] = Field(default_factory=list)
    incomplete_requirements: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    unresolved_critical_issues: List[str] = Field(default_factory=list)
    remaining_gaps: List[str] = Field(default_factory=list)
    decision: str = "READY"
    readiness_decision: str = "READY"  # READY, CONDITIONAL, NOT_READY
    readiness_rationale: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.readiness_decision and self.decision:
            self.readiness_decision = self.decision
        elif not self.decision and self.readiness_decision:
            self.decision = self.readiness_decision
        if not self.overall_score and self.overall_completeness:
            self.overall_score = self.overall_completeness
        elif not self.overall_completeness and self.overall_score:
            self.overall_completeness = self.overall_score


class TimelineEvent(BaseModel):
    """Chronological research activity timeline record."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    stage: str = "Stage 01 Planning"
    round_number: int = 1
    agent_role: str = ""
    action: str = ""
    event_type: str = ""
    status: str = "SUCCESS"
    summary: str = ""
    description: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.event_type and self.action:
            self.event_type = self.action
        elif not self.action and self.event_type:
            self.action = self.event_type
        if not self.description and self.summary:
            self.description = self.summary
        elif not self.summary and self.description:
            self.summary = self.description


class AgenticResearchState(BaseModel):
    """
    Complete shared research planning state holding all 13 agents' contributions,
    investigation timeline, reviews, and Stage 02 acquisition plan.
    """
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    original_query: str = ""
    original_question: str = ""
    current_round: int = 1
    max_rounds: int = 3
    status: str = "completed"
    readiness_decision: str = "READY"
    primary_domain: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Agent status records
    agents: Dict[str, AgentStatusRecord] = Field(default_factory=dict)
    agent_statuses: Dict[str, AgentStatusRecord] = Field(default_factory=dict)

    # Core structured findings
    intent: Optional[IntentAnalysis] = None
    intent_analysis: Optional[IntentAnalysis] = None
    domains: List[DiscoveredDomain] = Field(default_factory=list)
    discovered_domains: List[DiscoveredDomain] = Field(default_factory=list)
    subquestions: List[HierarchicalSubQuestion] = Field(default_factory=list)
    concepts: List[ScientificConcept] = Field(default_factory=list)
    scientific_concepts: List[ScientificConcept] = Field(default_factory=list)
    variables_and_equations: List[GoverningEquation] = Field(default_factory=list)
    governing_equations: List[GoverningEquation] = Field(default_factory=list)
    physical_processes: List[PhysicalProcessStep] = Field(default_factory=list)
    physical_process_chain: List[PhysicalProcessStep] = Field(default_factory=list)
    materials_and_components: List[MaterialOrComponent] = Field(default_factory=list)
    evidence_requirements: List[EvidenceRequirement] = Field(default_factory=list)
    cross_domain_connections: List[CrossDomainBridgeProposal] = Field(default_factory=list)
    cross_domain_bridges: List[CrossDomainBridgeProposal] = Field(default_factory=list)
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list)
    criticisms: List[AgentCriticism] = Field(default_factory=list)
    reviews: List[ReviewEvent] = Field(default_factory=list)
    review_events: List[ReviewEvent] = Field(default_factory=list)
    completeness: Optional[CompletenessEvaluation] = None
    completeness_evaluation: Optional[CompletenessEvaluation] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    all_findings: List[AgentFinding] = Field(default_factory=list)
    findings: List[AgentFinding] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.original_query and self.original_question:
            self.original_query = self.original_question
        elif not self.original_question and self.original_query:
            self.original_question = self.original_query
        
        if not self.agent_statuses and self.agents:
            self.agent_statuses = self.agents
        elif not self.agents and self.agent_statuses:
            self.agents = self.agent_statuses

        if not self.findings and self.all_findings:
            self.findings = self.all_findings
        elif not self.all_findings and self.findings:
            self.all_findings = self.findings

        if not self.discovered_domains and self.domains:
            self.discovered_domains = self.domains
        elif not self.domains and self.discovered_domains:
            self.domains = self.discovered_domains

        if not self.scientific_concepts and self.concepts:
            self.scientific_concepts = self.concepts
        elif not self.concepts and self.scientific_concepts:
            self.concepts = self.scientific_concepts

        if not self.governing_equations and self.variables_and_equations:
            self.governing_equations = self.variables_and_equations
        elif not self.variables_and_equations and self.governing_equations:
            self.variables_and_equations = self.governing_equations

        if not self.physical_process_chain and self.physical_processes:
            self.physical_process_chain = self.physical_processes
        elif not self.physical_processes and self.physical_process_chain:
            self.physical_processes = self.physical_process_chain

        if not self.cross_domain_bridges and self.cross_domain_connections:
            self.cross_domain_bridges = self.cross_domain_connections
        elif not self.cross_domain_connections and self.cross_domain_bridges:
            self.cross_domain_connections = self.cross_domain_bridges

        if not self.review_events and self.reviews:
            self.review_events = self.reviews
        elif not self.reviews and self.review_events:
            self.reviews = self.review_events

        if not self.completeness_evaluation and self.completeness:
            self.completeness_evaluation = self.completeness
        elif not self.completeness and self.completeness_evaluation:
            self.completeness = self.completeness_evaluation

        if not self.intent_analysis and self.intent:
            self.intent_analysis = self.intent
        elif not self.intent and self.intent_analysis:
            self.intent = self.intent_analysis

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        synonyms = {
            "domains": "discovered_domains",
            "discovered_domains": "domains",
            "concepts": "scientific_concepts",
            "scientific_concepts": "concepts",
            "variables_and_equations": "governing_equations",
            "governing_equations": "variables_and_equations",
            "physical_processes": "physical_process_chain",
            "physical_process_chain": "physical_processes",
            "cross_domain_connections": "cross_domain_bridges",
            "cross_domain_bridges": "cross_domain_connections",
            "reviews": "review_events",
            "review_events": "reviews",
            "all_findings": "findings",
            "findings": "all_findings",
            "agents": "agent_statuses",
            "agent_statuses": "agents",
            "intent": "intent_analysis",
            "intent_analysis": "intent",
            "completeness": "completeness_evaluation",
            "completeness_evaluation": "completeness",
            "original_query": "original_question",
            "original_question": "original_query",
        }
        syn = synonyms.get(name)
        if syn and syn in self.__class__.model_fields and getattr(self, syn, None) is not value:
            super().__setattr__(syn, value)
