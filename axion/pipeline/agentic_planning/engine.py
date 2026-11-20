"""Agentic Scientific Research Planning Engine.

Drives the coordinated 13-agent research planning system, runs multi-round deliberations,
and outputs an enriched QuestionSpec with embedded AgenticResearchState.
"""

from typing import Any, Dict, List, Optional
import logging
import time

from axion.pipeline.types import (
    QuestionSpec,
    SubQuestion,
)
from axion.pipeline.agentic_planning.types import (
    AgenticResearchState,
    AgentRole,
)
from axion.pipeline.agentic_planning.coordinator import ResearchCoordinatorAgent
from axion.pipeline.agentic_planning.agents.intent_agent import IntentUnderstandingAgent
from axion.pipeline.agentic_planning.agents.domain_agent import DomainDiscoveryAgent
from axion.pipeline.agentic_planning.agents.decomposition_agent import QuestionDecompositionAgent
from axion.pipeline.agentic_planning.agents.concepts_agent import ConceptsDiscoveryAgent
from axion.pipeline.agentic_planning.agents.variables_equations_agent import VariablesAndEquationsAgent
from axion.pipeline.agentic_planning.agents.process_mapping_agent import PhysicalProcessMappingAgent
from axion.pipeline.agentic_planning.agents.materials_technology_agent import MaterialsAndComponentsAgent
from axion.pipeline.agentic_planning.agents.evidence_requirements_agent import EvidenceRequirementsAgent
from axion.pipeline.agentic_planning.agents.cross_domain_agent import CrossDomainConnectionAgent
from axion.pipeline.agentic_planning.agents.knowledge_gap_agent import KnowledgeGapAgent
from axion.pipeline.agentic_planning.agents.critical_reviewer_agent import CriticalReviewerAgent
from axion.pipeline.agentic_planning.agents.completeness_evaluator_agent import CompletenessEvaluatorAgent

logger = logging.getLogger(__name__)


class AgenticPlanningEngine:
    """Coordinates and executes the 13 specialized research planning agents."""

    def __init__(self, llm_provider: Any = None, max_rounds: int = 3):
        self.llm_provider = llm_provider
        self.max_rounds = max_rounds

        # Initialize all 13 specialized agents
        self.coordinator = ResearchCoordinatorAgent(llm_provider)
        self.intent_agent = IntentUnderstandingAgent(llm_provider)
        self.domain_agent = DomainDiscoveryAgent(llm_provider)
        self.decomposition_agent = QuestionDecompositionAgent(llm_provider)
        self.concepts_agent = ConceptsDiscoveryAgent(llm_provider)
        self.variables_agent = VariablesAndEquationsAgent(llm_provider)
        self.process_agent = PhysicalProcessMappingAgent(llm_provider)
        self.materials_agent = MaterialsAndComponentsAgent(llm_provider)
        self.evidence_agent = EvidenceRequirementsAgent(llm_provider)
        self.cross_domain_agent = CrossDomainConnectionAgent(llm_provider)
        self.gap_agent = KnowledgeGapAgent(llm_provider)
        self.reviewer_agent = CriticalReviewerAgent(llm_provider)
        self.evaluator_agent = CompletenessEvaluatorAgent(llm_provider)

    def plan_research(self, question: str) -> AgenticResearchState:
        """Executes full multi-agent planning across bounded rounds."""
        start_time = time.time()
        logger.info(f"Starting Agentic Research Planning for question: '{question}'")

        # Initialize shared structured state
        state = self.coordinator.initialize_state(question)

        # -------------------------------------------------------------
        # ROUND 1: Multi-Perspective Scientific Discovery
        # -------------------------------------------------------------
        state.current_round = 1
        self.coordinator.log_timeline(
            state,
            event_type="ROUND_STARTED",
            description="Initiating Round 1: Multi-perspective domain, equation, and process discovery.",
            round_number=1,
        )

        # Execute Round 1 discovery agents in logical dependency order
        state = self.intent_agent.execute(state)
        state = self.domain_agent.execute(state)
        state = self.decomposition_agent.execute(state)
        state = self.concepts_agent.execute(state)
        state = self.variables_agent.execute(state)
        state = self.process_agent.execute(state)
        state = self.materials_agent.execute(state)
        state = self.evidence_agent.execute(state)
        state = self.cross_domain_agent.execute(state)

        # -------------------------------------------------------------
        # ROUND 2: Adversarial Scientific Audit & Gap Synthesis
        # -------------------------------------------------------------
        state.current_round = 2
        self.coordinator.log_timeline(
            state,
            event_type="ROUND_STARTED",
            description="Initiating Round 2: Adversarial equation audit, physical reality checks, and gap analysis.",
            round_number=2,
        )

        state = self.gap_agent.execute(state)
        state = self.reviewer_agent.execute(state)

        # -------------------------------------------------------------
        # ROUND 3: Quality Gatekeeping & Final Synthesis
        # -------------------------------------------------------------
        state.current_round = 3
        self.coordinator.log_timeline(
            state,
            event_type="ROUND_STARTED",
            description="Initiating Round 3: Systematic completeness evaluation and readiness decision.",
            round_number=3,
        )

        state = self.evaluator_agent.execute(state)
        state = self.coordinator.execute(state)

        elapsed = time.time() - start_time
        logger.info(
            f"Agentic Research Planning completed in {elapsed:.2f}s with readiness verdict: {state.readiness_decision} "
            f"({len(state.findings)} total findings across 13 agents)"
        )
        return state

    def synthesize_question_spec(self, state: AgenticResearchState) -> QuestionSpec:
        """Converts the AgenticResearchState into an enriched QuestionSpec for Stage 02."""
        # Convert hierarchical subquestions to pipeline SubQuestions
        subqs: List[SubQuestion] = []
        deps_dict: Dict[str, List[str]] = {}
        for hsq in state.subquestions:
            sq = SubQuestion(
                id=hsq.id,
                question=hsq.question,
                target_subject=hsq.target_domain or (state.primary_domain or "Interdisciplinary"),
                information_needed=hsq.information_needed,
                depends_on=hsq.depends_on,
                status="pending",
            )
            subqs.append(sq)
            if hsq.depends_on:
                deps_dict[hsq.id] = hsq.depends_on

        # Convert evidence requirements to list of strings
        research_reqs: List[str] = [
            f"{ev.information_needed} ({ev.verification_criteria})"
            for ev in state.evidence_requirements
        ]
        if not research_reqs:
            research_reqs = [f"Peer-reviewed research on {state.original_question[:40]}"]

        # Extract primary concepts and variables
        all_concepts = [c.name for c in state.scientific_concepts]
        domain_names = [d.name for d in state.discovered_domains]

        spec = QuestionSpec(
            raw_query=state.original_question,
            problem_type=state.intent_analysis.problem_type if state.intent_analysis else "mechanistic_modeling",
            domain_tags=domain_names if domain_names else ["Thermodynamics", "Materials Science"],
            entities=all_concepts[:10],
            extracted_concepts=all_concepts[:15],
            subquestions=subqs,
            subquestion_dependencies=deps_dict,
            research_requirements=research_reqs,
            agentic_research_state=state.model_dump(),
        )
        return spec
